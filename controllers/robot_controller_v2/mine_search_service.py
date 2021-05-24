import logging

from models.location import Location

log = logging.getLogger()


class MineService:
    def __init__(self, robot_id, supervisor):
        self.robot_id = robot_id
        self.supervisor = supervisor
        self.root_node = supervisor.getFromDef("mine0")
        self.found_mines = {}
        self.mines = {}
        self.fetch_mines()

    def fetch_mines(self):
        root_childrens = self.root_node.getField("children")
        log.debug(root_childrens.getCount())
        for i in range(100):
            node = root_childrens.getMFNode(i)
            if node is None:
                return
            if node.getDef().startswith("mine"):
                self.mines[node.getDef()] = node

    # Mayın ile ilgili olasılık gibi şeyler yaparsak buraya koyarız.
    def search_for_mine(self, location: Location, found_callback):
        if location is None:
            log.debug("Robot location is null. Returning.")
            return
        self.fetch_mines()
        for mine_node in self.mines.values():
            mine_loc = Location(mine_node.getPosition())
            if location.is_close(mine_loc):
                founded_mine = Mine(mine_node.getDef(), mine_loc, self.robot_id)
                if founded_mine.name in self.founded_mines:
                    return
                log.debug("Mine is close: {}".format(mine_loc))
                found_callback(MineFoundMessage(founded_mine.name, mine_loc))
                self.add_to_founded_mines(founded_mine)

    def process_founded_mine(self, message):
        mine_loc = Location.from_coords(**vars(message.content.mine_loc))
        mine = Mine(message.content.mine_name, mine_loc, message.robot_id)
        self.add_to_founded_mines(mine)

    def add_to_founded_mines(self, mine):
        log.debug("New mine founded: {}".format(mine))
        self.found_mines[mine.name] = mine


class MineFoundMessage:
    def __init__(self, mine_name, mine_loc):
        self.mine_name = mine_name
        self.mine_loc = mine_loc


class Mine:
    def __init__(self, name, loc, robot):
        self.name = name
        self.loc = loc
        self.discoverer_robot = robot

    def __str__(self):
        return "name: {}, discoverer_robot: {}, loc: {}".format(self.name, self.discoverer_robot, self.loc)
