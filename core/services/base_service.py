from decouple import config

class BaseAzureService:
    def __init__(self):
        self.use_azure = config('USE_AZURE_SERVICES', default='False') == 'True'
        if self.use_azure:
            self.setup_azure_connection()
    
    def setup_azure_connection(self):
        # Setup Azure connection if needed
        pass
    
    def safe_azure_operation(self, operation, *args, **kwargs):
        """Safely execute Azure operations only if Azure services are enabled"""
        if self.use_azure:
            return operation(*args, **kwargs)
        return None 