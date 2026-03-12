class AuditService:
    def __init__(self, data_store):
        self.ds = data_store
        
    def get_all_logs(self):
        return self.ds.audit_log
        
    def get_recent_logs(self, limit=20):
        return self.ds.audit_log[-limit:]
        
    def get_logs_by_action(self, action_type):
        return [entry for entry in self.ds.audit_log if entry.action == action_type]
        
    def get_logs_by_user(self, user_filter):
        return [entry for entry in self.ds.audit_log if user_filter.lower() in entry.user.lower()]
        
    def get_action_types(self):
        return list(set(e.action for e in self.ds.audit_log))
