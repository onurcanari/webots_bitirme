import logging

from models.location import Location
import time

log = logging.getLogger()


class MineService:
    def __init__(self, robot_id, supervisor):
        self.robot_id = robot_id
        self.supervisor = supervisor
        self.root_node = supervisor.getFromDef("mine0")
        self.found_mines = {}
        self.mines = {}
        self.start_time = time.time()
        self.mines_found = False
        self.fetch_mines()
    
    def fetch_mines(self):
        """ Rastgele oluşmuş mayınları getirir. """
        root_childrens = self.root_node.getField("children")
        for i in range(root_childrens.getCount()):
            node = root_childrens.getMFNode(i)
            if node is None:
                return
            if node.getDef().startswith("mine"):
                self.mines[node.getDef()] = node

    # Mayın ile ilgili olasılık gibi şeyler yaparsak buraya koyarız.
    def search_for_mine(self, location: Location, found_callback):
        """ Robotun konumunuyla mayınların konumumnu karşılaştırır. Mayınların bulunma sürelerini kaydeder. Her bulunan mayın için found_callback çalıştırılır. """
        if location is None:
            log.debug("Robot location is null. Returning.")
            return

        if self.mines_found:
            return

        if len(self.mines) == len(self.found_mines):
            with open("mines_found.txt", "a") as file:
                file.write(str(time.time() - self.start_time)+"\n")
            self.mines_found = True

            return

        for mine_node in self.mines.values():
            mine_loc = Location(mine_node.getPosition())
            if location.is_close(mine_loc):
                found_mine = Mine(mine_node.getDef(), mine_loc, self.robot_id)
                if found_mine.name in self.found_mines:
                    return
                log.debug("New mine found: {}".format(found_mine))
                found_callback(MineFoundMessage(found_mine.name, mine_loc))
                self.add_to_found_mines(found_mine)

    def process_found_mine(self, message):
        """ Mayını bulunan mayınlara kaydeder. """
        mine_loc = Location.from_coords(**vars(message.content.mine_loc))
        mine = Mine(message.content.mine_name, mine_loc, message.robot_id)
        self.add_to_found_mines(mine)

    def add_to_found_mines(self, mine):
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
