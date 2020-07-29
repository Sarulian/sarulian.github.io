import random
import requests
import json
import copy
import uuid
from pprint import pprint

def aoe(func, pack, *args):
    for uuid in pack:
        func(pack[uuid], *args)
    return

def get_all_attacks(monster):
    attacks = []
    for action in monster['actions']:
        if 'attack_bonus' in action:
            attacks.append(action['name'])
    return attacks

def roll_attack(enemy_ac, monster, attack_name, adv=False, dis=False):
    for action in monster['actions']:
        try:
            if action['name'] == attack_name:
                damage_totals = {'monster_name': monster['name'], 'name': attack_name}
                to_hit = roll_to_hit(action, adv=adv, dis=dis)
                damage_totals['to_hit'] = to_hit

                if to_hit >= enemy_ac:
                    damage_totals['hit'] = True

                    if to_hit == 20+action['attack_bonus']:
                        damage_totals['crit'] = True
                    else:
                        damage_totals['crit'] = False

                    damage_totals['dmg'] = []
                    for damage in action['damage']:
                        try:
                            die_str, die_mod = damage['damage_dice'].rsplit('+', 1)
                        except ValueError:
                            die_str = damage['damage_dice']
                            die_mod = 0
                        dmg = roll_dice(die_str, die_mod, crit=damage_totals['crit'])
                        #dmg = roll_dice(damage['damage_dice'], damage['damage_bonus'], crit=damage_totals['crit'])
                        dmg_type = damage['damage_type']['name']
                        damage_totals['dmg'].append({'type': dmg_type, 'dmg':dmg})
                        #if dmg_type in list(damage_totals['dmg']):
                        #    damage_totals['dmg'][dmg_type] += dmg
                        #else:
                        #    damage_totals['dmg'][dmg_type] = dmg
                else:
                    damage_totals['hit'] = False
                    damage_totals['crit'] = False
                    damage_totals['dmg'] = {}
                return damage_totals
        except KeyError as e:
            print(e)
            continue

def roll_to_hit(attack, adv=False, dis=False):
    roll_1 = roll_dice('1d20', attack['attack_bonus'], crit=False)
    roll_2 = roll_dice('1d20', attack['attack_bonus'], crit=False)
    if adv and dis:
        return roll_1
    elif adv:
        return max(roll_1, roll_2)
    elif dis:
        return min(roll_1, roll_2)
    else:
        return roll_1

def roll_dice(die_str, mod, crit=False):
    dice = parse_dice_string(die_str)
    total = int(mod)
    if crit:
        dice = [[die_roll[0]*2, die_roll[1]] for die_roll in dice]

    for die_roll in dice:
        for die in range(die_roll[0]):
            total += random.randint(1, die_roll[1])

    return total

def parse_dice_string(dice_str):
    roll_strings = dice_str.split('+')
    dice = []
    for roll_string in roll_strings:
        dice.append([int(num) for num in roll_string.split('d')])
    return dice

def load_monster(monster_name):
    url = 'http://www.dnd5eapi.co/api/monsters/' + monster_name
    info = requests.get(url).json()
    if info == {'error': 'Not found'}:
        return 'ERROR: monster not found in api'
    info['uuid'] = str(uuid.uuid4())
    info['max_hit_points'] = info['hit_points']
    info['temporary_hit_points'] = 0
    return info

def load_pack(monster_name, num):
    pack = {}
    monster_template = load_monster(monster_name)
    for i in range(num):
        monster = copy.deepcopy(monster_template)
        monster['uuid'] = str(uuid.uuid4())
        pack[monster['uuid']] = monster
    return pack

def apply_mighty_summoner(monster):
    extra_hp = 2 * int(monster["hit_dice"].split("d")[0])
    monster["max_hit_points"] = monster["max_hit_points"] + extra_hp
    monster["hit_points"]     = monster["hit_points"] + extra_hp
    return

def apply_damage(monster, dmg):
    if monster["hit_points"] <= 0:
        return
    dmg_to_hp = dmg - monster["temporary_hit_points"]
    if dmg_to_hp < 0:
        monster["temporary_hit_points"] = monster["temporary_hit_points"] - dmg
    else:
        monster["temporary_hit_points"] = 0
        monster["hit_points"] = max(
                monster["hit_points"] - dmg_to_hp,
                0
            )
    return

def apply_heal(monster, healing):
    if monster["hit_points"] <= 0:
        return
    monster["hit_points"] = min(
            monster["max_hit_points"],
            monster["hit_points"] + healing
        )
    return

def apply_tempHP(monster, tempHP):
    if monster["hit_points"] <= 0:
        return
    if monster["temporary_hit_points"] < tempHP:
        monster["temporary_hit_points"] = tempHP
    return

def format_stats(monster):
    speed_str  = ", ".join(["{} {}".format(k, v) for k, v in monster["speed"].items()])
    senses_str = ", ".join(["{} {}".format(k, v) for k, v in monster["senses"].items()])
    try:
        skills_str = ", ".join(["{}: {}".format(d["name"][7:],d["value"]) for d in monster["proficiencies"]])
    except KeyError:
        skills_str = "None"
    try:
        specials_str = "\n\n".join(["<b>{}</b>: {}<br><br>".format(d["name"], d["desc"]) for d in monster["special_abilities"]])
    except KeyError:
        specials_str = "None<br>"
    actions_str  = "\n\n".join(["<b>{}</b>: {}<br><br>".format(d["name"], d["desc"]) for d in monster["actions"]])

    monsterCleanInfo = """
    <html>
        <h2>{}</h2>
        <b>Armor Class:</b> {}<br>
        <b>Hit Points:</b> {}<br>
        <b>Speed:</b> {}<br>
        <table id="t01">
            <tr><b>
                <th>STR</th><th>DEX</th><th>CON</th><th>INT</th><th>WIS</th><th>CHA</th>
            </b></tr>
            <tr>
                <td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td>
            </tr>
            <tr>
                <td>({})</td><td>({})</td><td>({})</td><td>({})</td><td>({})</td><td>({})</td>
            </tr>
        </table>
        <p>
            <b>Skills:</b> {}<br>
            <b>Senses:</b> {}<br>
            <b>CR:</b> {}/{}<br>
            <hr>
            {}
            <hr>
            {}
        </p></html>""".format(
            monster["name"], monster["armor_class"], monster["hit_points"], speed_str,
            monster["strength"], monster["dexterity"], monster["constitution"], 
            monster["intelligence"], monster["wisdom"], monster["charisma"],
            mod(monster["strength"]), mod(monster["dexterity"]), mod(monster["constitution"]),
            mod(monster["intelligence"]), mod(monster["wisdom"]), mod(monster["charisma"]),
            skills_str, senses_str,
            str(float(monster["challenge_rating"]).as_integer_ratio()[0]),
            str(float(monster["challenge_rating"]).as_integer_ratio()[1]),
            specials_str, actions_str
        )
    return monsterCleanInfo

def mod(stat):
    return "{:+}".format(int((stat-10)/2))



class Pack:
    def __init__(self, animal, size):
        og_animal = Animal(animal)
        self.animals = [copy.deepcopy(og_animal) for i in range(size)]
        for i, animal in enumerate(self.animals):
            animal.info["name"] += " {}".format(i+1)
        self.chosen_attack = None
        self.info = self.animals[0].info

    def __str__(self):
        return "\n".join([str(animal) for animal in self.animals])

    def hit_points(self):
        hit_point_list = []
        for animal in self.animals:
            hit_point_list.append({
                "animal": animal.info["name"],
                "hitPoints": animal.info["hit_points"],
                "temporaryHP": animal.info["temporary_hit_points"],
            })
        hit_point_list = sorted(hit_point_list, key=lambda k: k["animal"])

        return hit_point_list

    def as_dict(self):
        return self.animals[0].info

    def attack(self, attack_name, ac, advantage, disadvantage):
        total_dmg = 0
        damage_results = []
        for animal in self.animals:

            self.chosen_attack = animal.attacks[attack_name]
            if advantage:
                self.chosen_attack.give_advantage()
            else:
                self.chosen_attack.remove_advantage()
            if disadvantage:
                self.chosen_attack.give_disadvantage()
            else:
                self.chosen_attack.remove_disadvantage()

            if animal.info["hit_points"] <= 0:
                continue
            dmg_dict = {}
            dmg_dict["name"] = animal.info["name"]
            dmg_dict["dmg"] = []
            to_hit, is_crit, dmgs = self.chosen_attack.attack()
            dmg_dict["to_hit"] = to_hit
            if to_hit >= ac:
                dmg_dict["hit"] = True
                if is_crit:
                    dmg_dict["crit"] = True
                else:
                    dmg_dict["crit"] = False
                for dmg in dmgs:
                    dmg_dict["dmg"].append({"dmg": dmg[0], "type": dmg[1]})
                total_dmg += dmg[0]
            else:
                dmg_dict["hit"] = False

            damage_results.append(dmg_dict)

        return damage_results

    def apply_mighty_summoner(self):
        extra_hp = 2 * int(self.info["hit_dice"].split("d")[0])
        for animal in self.animals:
            animal.info["max_hit_points"] = animal.info["max_hit_points"] + extra_hp
            animal.info["hit_points"] = animal.info["hit_points"] + extra_hp

    def apply_damage(self, dmg):
        self.animals.sort(key=lambda x: x.info["hit_points"] + x.info["temporary_hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            dmg_to_hp = dmg - animal.info["temporary_hit_points"]
            if dmg_to_hp < 0:
                animal.info["temporary_hit_points"] = animal.info["temporary_hit_points"] - dmg
            else:
                animal.info["temporary_hit_points"] = 0
                animal.info["hit_points"] = max(
                    animal.info["hit_points"] - dmg_to_hp,
                    0
                )
            return

    def apply_heal(self, healing):
        healing_left = healing
        self.animals.sort(key=lambda x: x.info["hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            animal.info["hit_points"] = min(
                animal.info["max_hit_points"],
                animal.info["hit_points"] + healing
            )
            return

    def apply_tempHP(self, tempHP):
        self.animals.sort(key=lambda x: x.info["temporary_hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            if animal.info["temporary_hit_points"] < tempHP:
                animal.info["temporary_hit_points"] = tempHP
            break

    def apply_damage_aoe(self, dmg):
        self.animals.sort(key=lambda x: x.info["hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            dmg_to_hp = dmg - animal.info["temporary_hit_points"]
            if dmg_to_hp < 0:
                animal.info["temporary_hit_points"] = animal.info["temporary_hit_points"] - dmg
            else:
                animal.info["temporary_hit_points"] = 0
                animal.info["hit_points"] = max(
                    animal.info["hit_points"] - dmg_to_hp,
                    0
                )

    def apply_heal_aoe(self, healing):
        self.animals.sort(key=lambda x: x.info["hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            animal.info["hit_points"] = min(
                animal.info["max_hit_points"], 
                animal.info["hit_points"] + healing
            )

    def apply_tempHP_aoe(self, tempHP):
        self.animals.sort(key=lambda x: x.info["hit_points"])
        for animal in self.animals:
            if animal.info["hit_points"] <= 0:
                continue
            animal.info["temporary_hit_points"] = max(
                animal.info["temporary_hit_points"], 
                tempHP
            )

    def format_animal_info(self):
        info = self.info
        speed_str  = ", ".join(["{} {}".format(k, v) for k, v in info["speed"].items()])
        senses_str = ", ".join(["{} {}".format(k, v) for k, v in info["senses"].items()])
        try:
            skills_str = ", ".join(["{}: {}".format(d["name"][7:],d["value"]) for d in info["proficiencies"]])
        except KeyError:
            skills_str = "None"
        try:
            specials_str = "\n\n".join(["<b>{}</b>: {}<br><br>".format(d["name"], d["desc"]) for d in info["special_abilities"]])
        except KeyError:
            specials_str = "None<br>"
        actions_str  = "\n\n".join(["<b>{}</b>: {}<br><br>".format(d["name"], d["desc"]) for d in info["actions"]])

        animalCleanInfo = """
        <html>
            <h2>{}</h2>
            <b>Armor Class:</b> {}<br>
            <b>Hit Points:</b> {}<br>
            <b>Speed:</b> {}<br>
            <table id="t01">
                <tr><b>
                    <th>STR</th><th>DEX</th><th>CON</th><th>INT</th><th>WIS</th><th>CHA</th>
                </b></tr>
                <tr>
                    <td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td><td>{:2d}</td>
                </tr>
                <tr>
                    <td>({})</td><td>({})</td><td>({})</td><td>({})</td><td>({})</td><td>({})</td>
                </tr>
            </table>
            <p>
                <b>Skills:</b> {}
                <br>
                <b>Senses:</b> {}
                <br>
                <b>CR:</b> {}/{}
                <br>
                <hr>
                {}
                <hr>
                {}
            </p>
            </html>""".format(
                info["name"][:-2],
                info["armor_class"],
                info["hit_points"],
                speed_str,
                info["strength"],
                info["dexterity"],
                info["constitution"],
                info["intelligence"],
                info["wisdom"],
                info["charisma"],
                mod(info["strength"]),
                mod(info["dexterity"]),
                mod(info["constitution"]),
                mod(info["intelligence"]),
                mod(info["wisdom"]),
                mod(info["charisma"]),
                skills_str,
                senses_str,
                str(float(info["challenge_rating"]).as_integer_ratio()[0]),
                str(float(info["challenge_rating"]).as_integer_ratio()[1]),
                specials_str,
                actions_str
            )
        return animalCleanInfo



if __name__ == '__main__':

    mon = load_monster('giant-toad')   # dict
    attacks = get_all_attacks(mon)     # list

    for attack in attacks:
        print(roll_attack(10, mon, attack))
