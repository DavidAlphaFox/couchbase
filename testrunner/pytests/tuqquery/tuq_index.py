import math

from tuqquery.tuq import QueryTests
from remote.remote_util import RemoteMachineShellConnection
from membase.api.rest_client import RestConnection
from membase.api.exception import CBQError

class QueriesViewsTests(QueryTests):

    FIELDS_TO_INDEX = ['name', 'job_title', 'join_yr']
    COMPLEX_FIELDS_TO_INDEX = ['VMs', 'tasks_points', 'skills']

    def setUp(self):
        super(QueriesViewsTests, self).setUp()
        self.num_indexes = self.input.param('num_indexes', 1)
        if self.num_indexes > len(self.FIELDS_TO_INDEX):
            self.input.test_params["stop-on-failure"] = True
            self.log.error("MAX NUMBER OF INDEXES IS 3. ALL TESTS WILL BE SKIPPED")
            self.fail('MAX NUMBER OF INDEXES IS 3. ALL TESTS WILL BE SKIPPED')

    def suite_setUp(self):
        super(QueriesViewsTests, self).suite_setUp()

    def tearDown(self):
        super(QueriesViewsTests, self).tearDown()

    def suite_tearDown(self):
        super(QueriesViewsTests, self).suite_tearDown()

    def test_simple_create_delete_index(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    view_name = "my_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (
                                            view_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    actual_result = self.run_cbq_query()
                    self._verify_results(actual_result['results'], [])
                    created_indexes.append(view_name)
                    self._verify_view_is_present(view_name, bucket)
                    self.assertTrue(self._is_index_in_list(bucket, view_name), "Index is not in list")
            finally:
                for view_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, view_name)
                    actual_result = self.run_cbq_query()
                    self._verify_results(actual_result['results'], [])
                    self.assertFalse(self._is_index_in_list(bucket, view_name), "Index is in list")

    def test_primary_create_delete_index(self):
        for bucket in self.buckets:
            self.query = "CREATE PRIMARY INDEX ON %s " % (bucket.name)
            actual_result = self.run_cbq_query()
            self._verify_results(actual_result['results'], [])
            self.assertTrue(self._is_index_in_list(bucket, "#primary"), "Index is not in list")

    def test_create_delete_index_with_query(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    view_name = "tuq_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (view_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    actual_result = self.run_cbq_query()
                    self._verify_results(actual_result['results'], [])
                    created_indexes.append(view_name)
                    self.test_case()
            except Exception, ex:
                content = self.cluster.query_view(self.master, "ddl_%s" % view_name, view_name, {"stale" : "ok"},
                                                  bucket="default", retry_time=1)
                self.log.info("Generated view has %s items" % len(content['rows']))
                raise ex
            finally:
                for view_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name,view_name)
                    actual_result = self.run_cbq_query()
                    self._verify_results(actual_result['results'], [])
                self.test_case()

    def test_explain(self):
        for bucket in self.buckets:
            try:
                self.query = "CREATE PRIMARY INDEX ON %s " % (bucket.name)
                self.run_cbq_query()
            except CBQError as ex:
                if str(ex).find("Primary index already exists") == -1:
                    raise ex
            self.query = "EXPLAIN SELECT * FROM %s" % (bucket.name)
            res = self.run_cbq_query()
            self.assertTrue(res["results"][0]["children"][0]["index"] == "#primary",
                            "Type should be #alldocs, but is: %s" % res["results"])

    def test_explain_query_count(self):
        for bucket in self.buckets:
            index_name = "my_index_child"
            try:
                self.query = "CREATE INDEX %s ON %s(VMs) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT count(VMs) FROM %s ' % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_query_group_by(self):
        for bucket in self.buckets:
            index_name = "my_index_child"
            try:
                self.query = "CREATE INDEX %s ON %s(VMs) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT count(VMs) FROM %s GROUP BY join_day' % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_query_array(self):
        for bucket in self.buckets:
            index_name = "my_index_arr"
            try:
                self.query = "CREATE INDEX %s ON %s(VMs) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT ARRAY vm.memory FOR vm IN VMs END AS vm_memories FROM %s' % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_query_meta(self):
        for bucket in self.buckets:
            index_name = "my_index_meta"
            try:
                self.query = "CREATE INDEX %s ON %s(meta(%s).type) " % (index_name, bucket.name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT name FROM %s WHERE meta(%s).type = "json"' % (bucket.name, bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_index_with_fn(self):
        for bucket in self.buckets:
            index_name = "my_index_fn"
            try:
                self.query = "CREATE INDEX %s ON %s(round(test_rate)) " % (index_name, bucket.name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN select name, round(test_rate) as rate from %s WHERE round(test_rate) = 2' % (bucket.name, bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()


    def test_explain_index_attr(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "my_attr_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (index_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    self.run_cbq_query()
                    self.query = "EXPLAIN SELECT * FROM %s WHERE %s = 'abc'" % (bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    res = self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.assertTrue(res["results"][0]["input"]["type"] == "filter",
                                    "Type should be fetch, but is: %s" % res["results"])
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["type"] == "scan",
                                    "Type should be scan, but is: %s" % res["results"])
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_non_index_attr(self):
        for bucket in self.buckets:
            index_name = "my_non_index"
            try:
                self.query = "CREATE INDEX %s ON %s(name) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = "EXPLAIN SELECT * FROM %s WHERE email = 'abc'" % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["type"] == "filter",
                                "Type should be fetch, but is: %s" % res["results"])
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["type"] == "scan",
                                "Type should be scan, but is: %s" % res["results"])
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] != index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_index_count_gn(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "my_aggr_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (index_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = "EXPLAIN SELECT COUNT(%s) FROM %s" % (self.FIELDS_TO_INDEX[ind-1], bucket.name)
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_index_aggr_gn(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "my_aggr_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (index_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = "EXPLAIN SELECT SUM(%s) FROM %s" % (self.FIELDS_TO_INDEX[ind-1], bucket.name)
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_index_join(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "join_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(name) " % (index_name, bucket.name)
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = "EXPLAIN SELECT employee.name, new_task.project FROM %s as employee JOIN %s as new_task" % (bucket.name, bucket.name)
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_index_unnest(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "join_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(tasks_ids) " % (index_name, bucket.name)
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = "EXPLAIN SELECT emp.name, task FROM %s emp UNNEST emp.tasks_ids task" % (bucket.name)
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_index_subquery(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "join_index%s" % ind
                    self.query = "CREATE INDEX %s ON %s(join_day) " % (index_name, bucket.name)
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = "EXPLAIN select task_name, (select sum(test_rate) cn from %s use keys ['query-1'] where join_day>2) as names from %s" % (bucket.name, bucket.name)
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_explain_childs_list_objects(self):
        for bucket in self.buckets:
            index_name = "my_index_child"
            try:
                self.query = "CREATE INDEX %s ON %s(VMs) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT VMs FROM %s ' % (bucket.name) +\
                        'WHERE ANY vm IN VMs SATISFIES vm.RAM > 5 AND vm.os = "ubuntu" end'
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_childs_objects(self):
        for bucket in self.buckets:
            index_name = "my_index_obj"
            try:
                self.query = "CREATE INDEX %s ON %s(tasks_points) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT tasks_points.task1 AS task from %s ' % (bucket.name) +\
                             'WHERE join_mo>7 and task_points > 0'
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_childs_objects_element(self):
        for bucket in self.buckets:
            index_name = "my_index_obj_el"
            try:
                self.query = "CREATE INDEX %s ON %s(tasks_points.task1) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT tasks_points.task1 AS task from %s ' % (bucket.name) +\
                             'WHERE join_mo>7 and  task_points.task1 > 0'
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_childs_list_element(self):
        for bucket in self.buckets:
            index_name = "my_index_list_el"
            try:
                self.query = "CREATE INDEX %s ON %s(skills[0]) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT DISTINCT skills[0] as skill' +\
                         ' FROM %s WHERE skills[0] = "abc"' % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_childs_list(self):
        for bucket in self.buckets:
            index_name = "my_index_list"
            try:
                self.query = "CREATE INDEX %s ON %s(skills) " % (index_name, bucket.name)
                self.run_cbq_query()
                self.query = 'EXPLAIN SELECT DISTINCT skills[0] as skill' +\
                         ' FROM %s WHERE skill[0] = "skill2010"' % (bucket.name)
                res = self.run_cbq_query()
                self.assertTrue(res["results"][0]["input"]["input"]["input"]["input"]["index"] == index_name,
                                "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                self.run_cbq_query()

    def test_explain_several_complex_objects(self):
        for bucket in self.buckets:
            created_indexes = []
            try:
                for ind in xrange(self.num_indexes):
                    index_name = "my_index_complex%s" % ind
                    self.query = "CREATE INDEX %s ON %s(%s) " % (index_name, bucket.name, self.FIELDS_TO_INDEX[ind-1])
                    self.run_cbq_query()
                    created_indexes.append(index_name)
                    self.query = 'EXPLAIN SELECT DISTINCT %s as complex FROM %s WHERE %s = "abc"' % (self.FIELDS_TO_INDEX[ind-1],
                                                                                                      bucket.name,
                                                                                                      self.FIELDS_TO_INDEX[ind-1])
                    res = self.run_cbq_query()
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == index_name,
                                    "Index should be %s, but is: %s" % (index_name,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_index_dates(self):
        for bucket in self.buckets:
            index_name = "my_index_date"
            try:
                self.query = "CREATE INDEX %s ON %s(" % (index_name, bucket.name) +\
                "str_to_millis(tostr(join_yr) || '-0' || tostr(join_mo) || '-0' || tostr(join_day))) "
                self.run_cbq_query()
            except Exception, ex:
                self.assertTrue(str(ex).find("Expression is not supported by indexing currently") != -1,
                                "Error message is %s." % str(ex))
            else:
                self.fail("Error message expected")

    def test_multiple_indexes_query_attr(self):
        index_name_prefix = 'auto_ind'
        for bucket in self.buckets:
            created_indexes = []
            try:
                for attr in ['join_day', 'join_mo']:
                    self.query = "CREATE INDEX %s_%s ON %s(%s) " % (index_name_prefix, attr,
                                                                    bucket.name, attr)
                    self.run_cbq_query()
                    created_indexes.append('%s_%s' % (index_name_prefix, attr))
                    self.query = 'SELECT name, join_day, join_mo FROM %s WHERE join_day>2 AND join_mo>3' % (bucket.name)
                    res = self.run_cbq_query()
                    full_list = self._generate_full_docs_list(self.gens_load)
                    expected_result = [{"name" : doc['name'], "join_mo" : doc['join_mo'], "join_day" : doc["join_day"]}
                                       for doc in full_list if doc['join_day'] > 2 and doc['join_mo'] > 3]
                    self._verify_results(sorted(res['results']), sorted(expected_result))
                    self.query = 'EXPLAIN SELECT name, join_day, join_mo FROM %s WHERE join_day>2 AND join_mo>3' % (bucket.name)
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == '%s_%s' % (index_name_prefix, attr),
                                    "Index should be %s_%s, but is: %s" % (index_name_prefix, attr,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def test_multiple_indexes_query_non_ind_attr(self):
        index_name_prefix = 'auto_ind'
        for bucket in self.buckets:
            created_indexes = []
            try:
                for attr in ['join_day', 'join_mo']:
                    self.query = "CREATE INDEX %s_%s ON %s(%s) " % (index_name_prefix, attr,
                                                                    bucket.name, attr)
                    self.run_cbq_query()
                    created_indexes.append('%s_%s' % (index_name_prefix, attr))
                    self.query = 'SELECT name, join_day, join_yr FROM %s WHERE join_yr>3' % (bucket.name)
                    res = self.run_cbq_query()
                    full_list = self._generate_full_docs_list(self.gens_load)
                    expected_result = [{"name" : doc['name'], "join_yr" : doc['join_yr'], "join_day" : doc["join_day"]}
                                       for doc in full_list if doc['join_yr'] > 3]
                    self._verify_results(sorted(res['results']), sorted(expected_result))
                    self.query = 'EXPLAIN SELECT name, join_day, join_yr FROM %s WHERE join_yr>3' % (bucket.name)
                    self.assertTrue(res["results"][0]["input"]["input"]["input"]["index"] == '%s_%s' % (index_name_prefix, attr),
                                    "Index should be %s_%s, but is: %s" % (index_name_prefix, attr,res["results"]))
            finally:
                for index_name in created_indexes:
                    self.query = "DROP INDEX %s.%s" % (bucket.name, index_name)
                    self.run_cbq_query()

    def _verify_view_is_present(self, view_name, bucket):
        ddoc, _ = RestConnection(self.master).get_ddoc(bucket.name, "ddl_%s" % view_name)
        self.assertTrue(view_name in ddoc["views"], "View %s wasn't created" % view_name)

    def _is_index_in_list(self, bucket, index_name):
        query = "SELECT * FROM system:indexes"
        res = self.run_cbq_query(query)
        for item in res['results']:
            if item['keyspace_id'] == bucket.name and item['name'] == index_name:
                return True
        return False
