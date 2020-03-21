import json

from flask import current_app


class Webpack(object):
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Mutate the application passed in as explained here:
        http://flask.pocoo.org/docs/0.10/extensiondev/

        :param app: Flask application
        :return: None
        """

        # Setup a few sane defaults.
        app.config.setdefault("WEBPACK_MANIFEST_PATH", "static/dist/manifest.json")

        self._set_asset_paths(app)

        # We only want to refresh the webpack stats in development mode,
        # not everyone sets this setting, so let's assume it's production.
        if app.config.get("DEBUG", False):
            app.before_request(self._refresh_webpack_stats)

        app.add_template_global(self.url_for_asset)

    def _set_asset_paths(self, app):
        """
        Read in the manifest json file which acts as a manifest for assets.
        This allows us to get the asset path as well as hashed names.

        :param app: Flask application
        :return: None
        """
        manifest_path = app.config["WEBPACK_MANIFEST_PATH"]

        with app.open_resource(manifest_path, "r") as manifest:
            self.assets = json.load(manifest)

    def _refresh_webpack_stats(self):
        """
        Refresh the webpack stats so we get the latest version. It's a good
        idea to only use this in development mode.

        :return: None
        """
        self._set_asset_paths(current_app)

    def url_for_asset(self, asset):
        return self.assets.get(asset)
