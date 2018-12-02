from envparse import env


CONFIG = {}


if env.bool("LOCK_SENSORS_PROD", default=False):
    import lock_sensors.common.settings.prod

    CONFIG.update(prod.CONFIG)
else:
    import lock_sensors.common.settings.dev

    CONFIG.update(dev.CONFIG)


if env.bool("LOCK_SENSORS_TESTING", default=False):
    import lock_sensors.common.settings.test

    CONFIG.update(test.CONFIG)