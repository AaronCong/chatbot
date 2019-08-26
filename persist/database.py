# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pymysql
from logging import getLogger
from typing import List, Dict

from deeppavlov.core.common.registry import register
from deeppavlov.core.models.estimator import Estimator

log = getLogger(__name__)


@register('mysql_database')
class MysqlDatabase:
    """
    Loads and trains sqlite table of any items (with name ``table_name``
    and path ``save_path``).

    Primary (unique) keys must be specified, all other keys are infered from data.
    Batch here is a list of dictionaries, where each dictionary corresponds to an item.
    If an item doesn't contain values for all keys, then missing values will be stored
    with ``unknown_value``.

    Parameters:
        save_path: sqlite database path.
        table_name: name of the sqlite table.
        primary_keys: list of table primary keys' names.
        keys: all table keys' names.
        unknown_value: value assigned to missing item values.
        **kwargs: parameters passed to parent :class:`~deeppavlov.core.models.estimator.Estimator` class.
    """

    def __init__(self, dbhost: str,
                 dbuser: str,
                 dbpass: str,
                 dbname: str,
                 table_name: str,
                 primary_keys: List[str],
                 keys: List[str] = None,
                 unknown_value: str = 'UNK',
                 *args, **kwargs) -> None:
        # super().__init__(save_path=save_path, *args, **kwargs)

        self.primary_keys = primary_keys
        if not self.primary_keys:
            raise ValueError("Primary keys list can't be empty")
        self.tname = table_name
        self.keys = keys
        self.unknown_value = unknown_value
        self.dbname = dbname
        self.dbhost = dbhost
        self.dbpass = dbpass
        self.dbuser = dbuser
        self.conn = pymysql.connect(host=dbhost, user=dbuser, password=dbpass, database=dbname)
        self.cursor = self.conn.cursor()
        if self._check_if_table_exists():
            log.info("Loading database from {}.".format(self.dbname))
            if not self.keys:
                self.keys = self._get_keys()
        else:
            log.info("Initializing empty database on {}.".format(self.dbname))

    def __call__(self, batch: List[Dict],
                 order_by: str = None,
                 ascending: bool = False) -> List[List[Dict]]:
        order = 'ASC' if ascending else 'DESC'
        if not self._check_if_table_exists():
            log.warn("Database is empty, call fit() before using.")
            return [[] for i in range(len(batch))]
        return [self._search(b, order_by=order_by, order=order) for b in batch]

    def _check_if_table_exists(self):
        self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"
                            " WHERE TABLE_SCHEMA='{}'"
                            " AND TABLE_NAME='{}';".format(self.dbname, self.tname))
        return bool(self.cursor.fetchall())

    def _search(self, kv, order_by, order):
        if not kv:
            # get all table content
            if order_by is not None:
                self.cursor.execute("SELECT * FROM {}".format(self.tname) +
                                    " ORDER BY {} {}".format(order_by, order))
            else:
                self.cursor.execute("SELECT * FROM {}".format(self.tname))
        else:
            keys = list(kv.keys())
            values = tuple(kv[k] for k in keys)
            where_expr = ' AND '.join('{}=%s'.format(k) for k in keys)
            if order_by is not None:
                self.cursor.execute("SELECT * FROM {}".format(self.tname) +
                                    " WHERE {}".format(where_expr) +
                                    " ORDER BY {} {}".format(order_by, order),
                                    values)
            else:
                print("SELECT * FROM {}".format(self.tname) +
                                    " WHERE {}".format(where_expr),
                                    values)
                self.cursor.execute("SELECT * FROM {}".format(self.tname) +
                                    " WHERE {}".format(where_expr),
                                    values)
        return [self._wrap_selection(s) for s in self.cursor.fetchall()]

    def _wrap_selection(self, selection):
        if not self.keys:
            self.keys = self._get_keys()
        return {f: v for f, v in zip(self.keys, selection)}

    def _get_keys(self):
        self.cursor.execute("desc {};".format(self.tname))
        return [info[0] for info in self.cursor]

    def _get_types(self):
        self.cursor.execute("desc {};".format(self.tname))
        return {info[0]: info[1] for info in self.cursor}

    def fit(self, data: List[Dict]) -> None:
        if not self._check_if_table_exists():
            self.keys = self.keys or list(set(k for d in data for k in d.keys()))
            types = ('integer' if type(data[0][k]) == int else 'text' for k in self.keys)
            self._create_table(self.keys, types)
        elif not self.keys:
            self.keys = self._get_keys()

        self._insert_many(data)

    def _create_table(self, keys, types):
        if any(pk not in keys for pk in self.primary_keys):
            raise ValueError("Primary keys must be from {}.".format(keys))
        new_types = ("{} {} primary key".format(k, t) if k in self.primary_keys else
                     "{} {}".format(k, t)
                     for k, t in zip(keys, types))
        self.cursor.execute("CREATE TABLE IF NOT EXISTS {} ({})"
                            .format(self.tname, ', '.join(new_types)))
        log.info("Created table with keys {}.".format(self._get_types()))

    def _insert_many(self, data):
        to_insert = {}
        to_update = {}
        for kv in filter(None, data):
            primary_values = tuple(kv[pk] for pk in self.primary_keys)
            record = tuple(kv.get(k, self.unknown_value) for k in self.keys)
            curr_record = self._get_record(primary_values)
            if curr_record:
                if primary_values in to_update:
                    curr_record = to_update[primary_values]
                if curr_record != record:
                    to_update[primary_values] = record
            else:
                to_insert[primary_values] = record

        if to_insert:
            fformat = ','.join(['%s'] * len(self.keys))
            self.cursor.executemany("INSERT into {}".format(self.tname) +
                                    " VALUES ({})".format(fformat),
                                    to_insert.values())
        if to_update:
            for record in to_update.values():
                self._update_one(record)

        self.conn.commit()

    def _get_record(self, primary_values):
        ffields = ', '.join(self.keys) or '*'
        where_expr = ' AND '.join("{} = '{}'".format(pk, v)
                                  for pk, v in zip(self.primary_keys, primary_values))
        fetched = self.cursor.execute("SELECT {} FROM {}".format(ffields, self.tname) +
                                      " WHERE {}".format(where_expr)).fetchone()
        if not fetched:
            return None
        return fetched

    def _update_one(self, record):
        set_expr = ', '.join("{} = '{}'".format(k, v)
                             for k, v in zip(self.keys, record)
                             if k not in self.primary_keys)
        where_expr = ' AND '.join("{} = '{}'".format(k, v)
                                  for k, v in zip(self.keys, record)
                                  if k in self.primary_keys)
        self.cursor.execute("UPDATE {}".format(self.tname) +
                            " SET {}".format(set_expr) +
                            " WHERE {}".format(where_expr))

    def save(self):
        pass

    def load(self):
        pass
