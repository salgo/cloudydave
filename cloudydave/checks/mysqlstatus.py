from copy import copy


class MysqlstatusCheck(object):
    def test(self, cd, host, params):
        try:
            import MySQLdb
        except ImportError:
            cd.log('mysqlstatus::ImportError', 'unable to import required '
                                               'module MySQLdb')
            return False

        report = copy(cd.basereport)
        report['test'] = 'mysqlstatus'
        result = {}

        bresult = False

        if not('port' in params):
            params['port'] = 3306

            try:
                db = MySQLdb.connect(host=host,
                                     user=params['user'],
                                     passwd=params['password'])
                cursor = db.cursor()
                cursor.execute("SHOW GLOBAL STATUS")
                tresult = cursor.fetchall()

                stats = ['Created_tmp_disk_tables', 'Connections',
                         'Max_used_connections', 'Open_files',
                         'Slow_queries', 'Table_locks_waited',
                         'Threads_connected']

                for stat in tresult:
                    if stat[0] in stats:
                        result[stat[0]] = stat[1]
                bresult = True

            except MySQLdb.OperationalError:
                pass

        for key in result:
            report.update({'key': key, 'value': result[key]})
            cd.log_result(report)

        return bresult