from rest_framework.renderers import BrowsableAPIRenderer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    @property
    def template(self):
        return "restapi/api.html"
