import logging

from models.location import Location

log = logging.getLogger()


class MineService:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.root_node = supervisor.getFromDef("mine0")
        self.mines = []

        root_childrens = self.root_node.getField("children")
        log.debug("MINESERVICE")
        log.debug(root_childrens.getCount())
        for i in range(root_childrens.getCount()):
            node = root_childrens.getMFNode(i)
            log.debug(node)
            if node.getDef().startswith("mine"):
                self.mines.append(node)

        log.debug(MineService.__class__.__name__ + "MineService: " + str(self.mines))

    # Mayın ile ilgili olasılık gibi şeyler yaparsak buraya koyarız.
    def search_for_mine(self, location, found_callback):
        if location is None:
            return

        for mine_node in self.mines:
            mine_loc = Location(mine_node.getPosition())
            if location.is_close(mine_loc):
                found_callback(MineFoundMessage(mine_node.getDef(), mine_loc))


class MineFoundMessage:
    def __init__(self, mine_name, mine_loc):
        self.mine_name = mine_name
        self.mine_loc = mine_loc
