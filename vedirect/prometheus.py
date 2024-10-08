# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Exports fields as Prometheus gauges and enums."""

import logging
import enum
import time
import pint
import prometheus_client

from . import defs

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

_UNITS = {
    '%': 'percent',
    '°C': 'celcius',
    '0.01 kWh': 'DWh',
}

class Filter:
    def __init__(self):
        self._acc = None
        self._tau = 0.05

    def step(self, v: float) -> float:
        if self._acc is None:
            self._acc = v

        self._acc = self._acc * (1 - self._tau) + v * self._tau
        return self._acc

def _is_enum(v: object) -> bool:
    try:
        return issubclass(v, enum.Enum)
    except TypeError:
        return False

class Exporter:
    def __init__(self):
        self._metrics = None
        self._filters = {}

    def _config(self, fields):
        metrics = {}
        labels = ['model', 'product_id']

        for f in defs.FIELDS:
            label = f.label.replace('#', '')
            name = 'victron_%s' % label.lower()
            kind = f.kind()
            if isinstance(kind, pint.Quantity):
                unit = str(kind.units)
            else:
                unit = _UNITS.get(f.unit, f.unit)

            if unit == 'hour * watt':
                unit = 'wh'

            if kind == str:
                metrics[f.label] = prometheus_client.Info(name, f.description, labelnames=labels)
            elif _is_enum(kind):
                states = [x.name.lower() for x in kind]
                metrics[f.label] = prometheus_client.Enum(name, f.description, labelnames=labels, states=states)
                metrics[f.label + '_value'] = prometheus_client.Gauge(name + '_value', f.description, labelnames=labels)
            else:
                metrics[f.label] = prometheus_client.Gauge(name, f.description, labelnames=labels, unit=unit)

        updated = prometheus_client.Gauge('victron_updated', 'Last time a block was received from the device', labelnames=labels)
        blocks = prometheus_client.Counter('victron_blocks', 'Number of blocks received from the device', labelnames=labels)

        return metrics, updated, blocks

    def export(self, fields):
        if self._metrics is None:
            self._metrics, self._updated, self._blocks = self._config(fields)

        # Validate required fields before proceeding
        pid = fields.get('PID', 'unknown_pid')
        bmv = fields.get('BMV', 'unknown_bmv')

        logging.debug(f"Fields received: {fields}")
        logging.debug(f"PID: {pid}, BMV: {bmv}")

        if not pid or not bmv:
            logging.warning(f"Missing 'PID' or 'BMV' in fields: {fields}")

        try:
            self._updated.labels(model=bmv, product_id=pid).set(time.time())
            self._blocks.labels(model=bmv, product_id=pid).inc()
            logging.info(f"Metrics for PID: {pid} and BMV: {bmv} updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update metrics for PID and BMV due to: {e}")

        for label, value in fields.items():
            if label in self._metrics:
                try:
                    gauge = self._metrics[label]
                    if isinstance(value, pint.Quantity):
                        f = self._filters.setdefault(label, Filter())
                        m = f.step(value.m)
                        gauge.labels(model=bmv, product_id=pid).set(round(m, 3))
                    elif isinstance(gauge, prometheus_client.Info):
                        gauge.labels(model=bmv, product_id=pid).info({label.lower().replace('#', ''): value})
                    elif isinstance(gauge, prometheus_client.Enum):
                        gauge.labels(model=bmv, product_id=pid).state(value.name.lower())
                        self._metrics[label + '_value'].labels(model=bmv, product_id=pid).set(value.value)
                    elif isinstance(value, int):
                        gauge.labels(model=bmv, product_id=pid).set(value)
                    else:
                        logging.debug(f"Unhandled value type for {label}: {value}")
                except Exception as e:
                    logging.error(f"Failed to export {label} due to: {e}")

