def get_all_groups(self):
    try:
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT group_num FROM students ORDER BY group_num")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return []
    finally:
        if self.conn:
            self.conn.close()

def get_students_by_group(self, group):
    try:
        self.connect()
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE group_num = %s ORDER BY fullname", (group,))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return []
    finally:
        if self.conn:
            self.conn.close()