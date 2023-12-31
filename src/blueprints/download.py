from flask import request, jsonify, render_template, Blueprint
from exts import logger, config, qb, m_DBconnector, broadcast_map
# from lib.addqbTask import AddqbTask
from lib.models import *

anime_config = config.get('DOWNLOAD')
qb_config = config.get('QB')

bp = Blueprint("download", __name__, url_prefix="/download")
# qb = AddqbTask(qb_config, logger, anime_config)


@bp.route("/", methods=['GET'])
def index():
    completed_torrent_list = qb.get_completed_torrent_list()
    if completed_torrent_list is not None:
        for torrent in completed_torrent_list:
            update_anime_task_qb_task_status_by_torrent_name(torrent["hash"], 1)

    logger.info("[BP][DOWNLOAD] index success, url: /download/")
    return render_template("download.html", broadcast_map=broadcast_map)

@bp.route("/get_qb_download_progress", methods=['GET'])
def get_qb_download_progress():
    torrent_web_info_list = []
    task_list = query_anime_task_by_condition(qb_task_status=0)
    if len(task_list) == 0:
        return jsonify({"code": 200, "message": "subcribe_anime", "data": torrent_web_info_list})
    
    anime_list = query_anime_list_by_condition()
    anime_id_to_name_map = dict()
    for a in anime_list:
        anime_id_to_name_map[a["mikan_id"]] = a["anime_name"]
    
    for task in task_list:
        mikan_id = task['mikan_id']
        anime_name = anime_id_to_name_map[mikan_id]
        episode = task['episode']
        torrent_name = task['torrent_name']
        torrent_web_info = qb.get_torrent_web_info(torrent_name)
        if torrent_web_info is not None:
            torrent_web_info['mikan_id'] = mikan_id
            torrent_web_info['anime_name'] = anime_name
            torrent_web_info['episode'] = episode
            torrent_web_info['torrent_name'] = torrent_name
            torrent_web_info_list.append(torrent_web_info)
        else:
            continue
    return jsonify({"code": 200, "message": "subcribe_anime", "data": torrent_web_info_list})

def get_torrent_web_info(mikan_id, episode):   
    sql = 'select torrent_name from anime_task where mikan_id={} and episode={}'.format(mikan_id, episode)
    torrent_name = m_DBconnector.execute(sql)

    if len(torrent_name) == 0:
        logger.warning("[BP][get_torrent_web_info] can't find torrent_name by mikan_id: {}, episode: {}".\
                     format(mikan_id, episode))
        return
    
    torrent_name = torrent_name[0][0]
    torrent_web_info = qb.get_torrent_web_info(torrent_name)
    logger.debug("[BP][get_torrent_web_info] get torrent_web_info: {} ".format(torrent_web_info))
    return torrent_web_info

@bp.route("/delete_task", methods=['POST'])
def delete_task():
    mikan_id = request.args.get("mikan_id")
    episode = request.args.get("episode")

    if mikan_id is None:
        logger.error("[BP][get_torrent_web_info] miss mikan_id")
        return jsonify({"code": 400, "message": "failed to get torrent info, missing mikan_id", "data": None})
    if episode is None:
        logger.error("[BP][get_torrent_web_info] miss episode")
        return jsonify({"code": 400, "message": "failed to get torrent info, missing episode", "data": None})
    
    sql = 'select torrent_name from anime_task where mikan_id={} and episode={}'.format(mikan_id, episode)
    torrent_name = m_DBconnector.execute(sql)

    if len(torrent_name) == 0:
        logger.warning("[BP][get_torrent_web_info] can't find torrent_name by mikan_id: {}, episode: {}".\
                     format(mikan_id, episode))
        return jsonify({"code": 400, "message": "torrent is not exist", "data": None})
    
    torrent_name = torrent_name[0][0]
    qb.del_torrent(torrent_name)

    sql = 'DELETE FROM anime_task WHERE torrent_name="{}"'.format(torrent_name)
    m_DBconnector.execute(sql)
    return jsonify({"code": 200, "message": "delet torrent successfully", "data": None})

@bp.route("/delete_task_by_torrent_name", methods=['POST'])
def delete_task_by_torrent_name():
    torrent_name = request.args.get("torrent_name")
    qb.del_torrent(torrent_name)
    delete_anime_task_by_condition(torrent_name=torrent_name)
    return jsonify({"code": 200, "message": "delete_task_by_torrent_name", "data": None})

@bp.route("/pause_task_by_torrent_name", methods=['POST'])
def pause_task_by_torrent_name():
    torrent_name = request.args.get("torrent_name")
    qb.pause_qb_task(torrent_name)
    return jsonify({"code": 200, "message": "pause_task_by_torrent_name", "data": None})

@bp.route("/resume_task_by_torrent_name", methods=['POST'])
def resume_task_by_torrent_name():
    torrent_name = request.args.get("torrent_name")
    qb.resume_qb_task(torrent_name)
    return jsonify({"code": 200, "message": "pause_task_by_torrent_name", "data": None})

@bp.route("/pause_seeding_by_torrent_name", methods=['POST'])
def pause_seeding_by_torrent_name():
    torrent_name = request.args.get("torrent_name")
    qb.pause_seeding(torrent_name)
    return jsonify({"code": 200, "message": "pause_seeding_task_by_torrent_name", "data": None})

@bp.route("/pause_seeding_all", methods=['GET'])
def pause_seeding_all():
    qb.pause_seeding_all()
    return jsonify({"code": 200, "message": "pause_seeding_all", "data": None})

@bp.route("/get_max_active_downloads", methods=['GET'])
def get_max_active_downloads():
    max_active_downloads = qb.get_max_active_downloads()
    return jsonify({"code": 200, "message": "max_active_downloads", "data": max_active_downloads})

@bp.route("/modify_max_active_downloads", methods=['POST'])
def modify_max_active_downloads():
    nums = request.args.get("nums")
    qb.modify_max_active_downloads(nums)
    return jsonify({"code": 200, "message": "modify_max_active_downloads", "data": None})