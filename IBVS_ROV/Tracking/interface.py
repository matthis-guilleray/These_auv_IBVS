from .common import utilsLogger as logMod


class NodeInterface:
    _log = logMod.loggerCreate("Node Interface")

    def __init__(self):
        self.log.info("Node creation")
        pass

    
    def log(self, data, verbose):
        match verbose:
            case "debug":
                self._log.debug(data)
            case "info":
                self._log.info(data)
            case "warning":
                self._log.warning(data)
            case "error":
                self._log.error(data)


    def publish(self, topic, data, verbose = "info", **kwargs):
        self.log(f"Topic : {topic}", verbose=verbose)
        self.log(f"Topic : {data}", verbose=verbose)
        if (kwargs):
            self.log(kwargs, verbose=verbose)
        