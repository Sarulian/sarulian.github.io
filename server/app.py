from flask import Flask, jsonify, request
from flask_cors import CORS
import DnDBattles as dnd
import re
from pprint import pprint


# configuration
DEBUG = True

ANIMALS = [
    "adult-black-dragon",
    "brown-bear",
    "constrictor-snake",
    "dire-wolf",
    "draft-horse",
    "elk",
    "flying-snake",
    "giant-elk",
    "giant-frog",
    "giant-constrictor-snake",
    "wolf"
]

pack = None

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/', methods=['GET', 'POST'])
def load_pack():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        req_dict = request.get_json()
        pack = dnd.load_pack(req_dict['name'], req_dict['numAnimals'])
        if bool(int(req_dict['mighty'])):
            dnd.aoe(dnd.apply_mighty_summoner, pack)
        monster = next(iter(pack.values()))
        response_object['animalInfo'] = pack
        response_object['animalText'] = dnd.format_stats(monster)
        response_object['attackNames'] = dnd.get_all_attacks(monster)
    return jsonify(response_object)

@app.route('/animals', methods=['GET'])
def get_animals():
    return jsonify(ANIMALS)

@app.route('/hitpoints', methods=['GET', 'POST'])
def hitpoints():
    if request.method == 'POST':
        req_dict = request.get_json()
        pack = req_dict['pack']
        damage_info = req_dict['damageInfo']
        selected_rows = damage_info['selectedRows']
        if selected_rows == []:
            uuids = pack.keys()
        else:
            uuids = [d['uuid'] for d in selected_rows]

        if damage_info["type"] == "damage":
            for uuid in uuids:
                dnd.apply_damage(pack[uuid], damage_info["hitPointsMod"])
        elif damage_info["type"] == "heal":
            for uuid in uuids:
                dnd.apply_heal(pack[uuid], damage_info["hitPointsMod"])
        elif damage_info["type"] == "tempHP":
            for uuid in uuids:
                dnd.apply_tempHP(pack[uuid], damage_info["hitPointsMod"])

    hit_point_list = [{'uuid': mon['uuid'], 'name': mon['name'], 'hitPoints': mon['hit_points'], 'temporaryHP': mon['temporary_hit_points']} for k, mon in pack.items()]

    payload = {
        'hitPointList': hit_point_list,
        'pack': pack
    }
    return jsonify(payload)

@app.route('/attack', methods=['GET', 'POST'])
def attack():
    response_object = {'status': 'success'}

    if request.method == 'POST':
        req_dict = request.get_json()
        pack = req_dict['pack']
        attack_info = req_dict['attackInfo']
        #if pack is None:
        #    response_object['attackText'] = 'You must first conjure animals!'
        #    return jsonify(response_object)

        # Load current options for attack
        #
        selected_rows = attack_info['selectedRows']
        if selected_rows == []:
            uuids = pack.keys()
        else:
            uuids = [d['uuid'] for d in selected_rows]

        adv    = bool(int(attack_info['advantage']))
        dis    = bool(int(attack_info['disadvantage']))
        ac     = attack_info['enemyAC'] 
        attack = attack_info['attackName'] 

        add_die_num = int(attack_info['addDieNum'])
        add_die_max = int(attack_info['addDieMax'])
        add_die_mod = int(attack_info['addDieMod'])
        add_die_type =    attack_info['addDieType']

        die_str = "{}d{}".format(add_die_num, add_die_max)

        dmg_results = []
        for uuid in uuids:
            if pack[uuid]['hit_points'] > 0:
                #pprint(pack[uuid])
                result = dnd.roll_attack(ac, pack[uuid], attack, adv=adv, dis=dis)
                if result is None:
                    continue
                dmg_results.append(result)

        add_total = 0
        for result in dmg_results:
            if result["hit"]:
                if result["crit"]:
                    result["additional"] = dnd.roll_dice(die_str, add_die_mod, crit=(add_die_type == "Additional Damage"))
                else:
                    result["additional"] = dnd.roll_dice(die_str, add_die_mod, crit=False)
                add_total += result["additional"]

        dmg_totals = {}
        total_hits = 0
        outputAttack = []
        outputAttack.append("<div class=\"attack-table\">")
        outputAttack.append("<table>")
        for result in dmg_results:
            outputAttack.append("<tr>")
            outputAttack.append("<td>{} attacks with <i>{}</i>...</td>".format(result["monster_name"], attack))
            if result["hit"] == False:
                outputAttack.append(
                    "<td>{} misses!</td><td></td><td></td>".format(result["to_hit"])
                )
            else:
                total_hits += 1
                outputAttack.append("<td>")
                if result["crit"]:
                    outputAttack.append("<span class=\"crit\">")
                    outputAttack.append("{} crits!".format(result["to_hit"]))
                    outputAttack.append("</span>")
                else:
                    outputAttack.append("{} hits!".format(result["to_hit"]))
                outputAttack.append("</td>")

                outputAttack.append("<td>")
                for dmg in result["dmg"]:
                    outputAttack.append("{} {} damage!<br>".format(dmg["dmg"], dmg["type"].lower()))
                    if dmg["type"] not in dmg_totals.keys():
                        dmg_totals[dmg["type"]] = [dmg["dmg"]]
                    else:
                        dmg_totals[dmg["type"]].append(dmg["dmg"])
                outputAttack.append("</td>")

                if add_die_type != 'None':
                    outputAttack.append("<td>")
                    outputAttack.append("{} {}".format(result["additional"], add_die_type))
                    outputAttack.append("</td>")

            outputAttack.append("</tr>")
        outputAttack.append("</table>")
        outputAttack.append("</div>")

        summaryText = []
        summaryText.append("Successful hits: {}<br>".format(total_hits))
        all_dmg = 0
        for dmg_type, dmg in dmg_totals.items():
            summaryText.append("<span class=\"tab\">")
            summaryText.append("<i>{}:</i> <b>{} damage</b><br>".format(dmg_type, sum(dmg)))
            summaryText.append("</span>")
            all_dmg += sum(dmg)
        if add_total > 0 and add_die_type == "Additional Damage":
            summaryText.append("<span class=\"tab\">")
            summaryText.append("<i>Additional:</i> <b>{} damage</b><br>".format(add_total))
            summaryText.append("</span>")
            all_dmg += add_total
        summaryText.append("<br>")
        summaryText.append("<h5>Total: {} damage</h5>".format(all_dmg))
        summaryText.append("<hr>")

        outputAttack = summaryText + outputAttack

        response_object["attackText"] = "".join(outputAttack)
    return jsonify(response_object)

if __name__ == '__main__':
    app.run(host= '0.0.0.0')

