import sys
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from exts import db
from .common import *
from .logManager import m_LogManager

logger = m_LogManager.getLogObj(sys.argv[0])

class AnimeList(db.Model):
    __tablename__ = "anime_list"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    anime_name = db.Column(db.String(80), nullable=True, unique=True)
    mikan_id = db.Column(db.Integer, nullable=True, unique=True)
    update_day = db.Column(db.Integer, nullable=True, comment='剧场版和ova为8')
    img_url = db.Column(db.String(40), nullable=False)
    anime_type = db.Column(db.Integer, nullable=True, comment='0为番剧,1为剧场版,2为ova')
    subscribe_status = db.Column(db.Integer, nullable=True, comment='0为未订阅,1为已订阅')


class AnimeSeed(db.Model):
    __tablename__ = "anime_seed"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mikan_id = db.Column(db.Integer, nullable=False)
    subgroup_id = db.Column(db.Integer, nullable=False)
    episode = db.Column(db.Integer, nullable=False)
    seed_name = db.Column(db.String(200), nullable=False)
    seed_url = db.Column(db.String(200), nullable=False, unique=True)
    seed_status = db.Column(db.Integer, nullable=True, comment='0为未使用,1为已使用')
    seed_size = db.Column(db.String(200), nullable=False)

class AnimeTask(db.Model):
    __tablename__ = "anime_task"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mikan_id = db.Column(db.Integer, nullable=False)
    qb_task_status = db.Column(db.Integer,comment='qb任务状态 0表示待下载 1表示下载成功')
    episode = db.Column(db.Integer, nullable=False)
    torrent_name = db.Column(db.String(200), nullable=False)


class AnimeBroadcast(db.Model):
    __tablename__ = "anime_broadcast"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mikan_id = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=True, comment='播出年份')
    season = db.Column(db.Integer, nullable=True, comment='播出季度,春夏秋冬对应1234')

class AnimeSubgroup(db.Model):
    __tablename__ = "anime_subgroup"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subgroup_id = db.Column(db.Integer, nullable=True, unique=True)
    subgroup_name = db.Column(db.String(40), nullable=True)

class AnimeFilter(db.Model):
    __tablename__ = "anime_filter"
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mikan_id = db.Column(db.Integer, nullable=True)
    filter_type = db.Column(db.String(200), nullable=True)
    filter_val = db.Column(db.Integer, nullable=True)
    object = db.Column(db.Integer, default=0, comment='filter类型 0表示local 1表示global')

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.warning("[MODELS] session_commit failed, error: {}".format(e))
        return False
    else:
        return True

def insert_data_to_anime_list(mikan_id, anime_name="", img_url="", update_day="8", anime_type="0", subscribe_status="0"):
    logger.info("[MODELS] insert_data_to_anime_list, anime_name :{}, mikan_id: {}, update_day: {}, anime_type: {}, subscribe_status: {}".format(anime_name, mikan_id, update_day, anime_type, subscribe_status))

    anime_list = AnimeList(anime_name=anime_name, mikan_id=mikan_id, img_url=img_url, update_day=update_day, anime_type=anime_type, subscribe_status=subscribe_status)
    db.session.add_all([anime_list])
    return session_commit()

def insert_data_to_anime_seed(mikan_id, episode, seed_url, subgroup_id, seed_name, seed_status, seed_size):
    logger.info("[MODELS] insert_data_to_anime_seed, mikan_id: {}, subgroup_id: {}, episode: {}, seed_name: {}, seed_url: {}, seed_status: {}, seed_size: {}".format(mikan_id, subgroup_id, episode, seed_name, seed_url, seed_status, seed_size))

    anime_seed = AnimeSeed(mikan_id=mikan_id, episode=episode, seed_url=seed_url, subgroup_id=subgroup_id, seed_name=seed_name, seed_status=seed_status, seed_size = seed_size)
    db.session.add_all([anime_seed])
    return session_commit()

def insert_data_to_anime_task(mikan_id, episode, torrent_name, qb_task_status):
    logger.info("[MODELS] insert_data_to_anime_task, mikan_id: {}, episode: {}, torrent_name: {}, qb_task_status".format(mikan_id, episode, torrent_name, qb_task_status))

    anime_task = AnimeTask(mikan_id=mikan_id, episode=episode, torrent_name=torrent_name, qb_task_status=qb_task_status)
    db.session.add_all([anime_task])
    return session_commit()

def insert_data_to_anime_broadcast(mikan_id, year, season):
    logger.info("[MODELS] insert_data_to_anime_broadcast, mikan_id: {}, year: {}, season: {}".format(mikan_id, year, season))

    anime_broadcast = AnimeBroadcast(mikan_id=mikan_id, year=year, season=season)
    db.session.add_all([anime_broadcast])
    return session_commit()

def insert_data_to_anime_subgroup(subgroup_id, subgroup_name):
    logger.info("[MODELS] insert_data_to_anime_subgroup, subgroup_id: {}, subgroupo_name: {}".format(subgroup_id, subgroup_name))

    anime_subgroup = AnimeSubgroup(subgroup_id=subgroup_id, subgroup_name=subgroup_name)
    db.session.add_all([anime_subgroup])
    return session_commit()

def query_anime_list_by_condition(anime_name='', mikan_id=-1, img_url='', update_day=-1, anime_type=-1, subscribe_status=-1):
    log_info_str = "[MODELS] query_anime_list_by_condition,"
    if anime_name != '':
        log_info_str += " anime_name: {},".format(anime_name)
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if img_url != '':
        log_info_str += " img_url: {},".format(img_url)
    if update_day != -1:
        log_info_str += " update_day: {},".format(update_day)
    if anime_type != -1:
        log_info_str += " anime_type: {},".format(anime_type)
    if subscribe_status != -1:
        log_info_str += " subscribe_status: {},".format(subscribe_status)
    logger.info(log_info_str[:-1])
    
    session = db.session.query(AnimeList)
    if anime_name != '':
        session = session.filter_by(anime_name=anime_name)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if img_url != '':
        session = session.filter_by(img_url=img_url)
    if update_day != -1:
        session = session.filter_by(update_day=update_day)
    if anime_type != -1:
        session = session.filter_by(anime_type=anime_type)
    if subscribe_status != -1:
        session = session.filter_by(subscribe_status=subscribe_status)
    result = session.all()
    list = []
    for data in result:
        dic = {
            "index"            : data.index,
            "anime_name"       : data.anime_name,
            "mikan_id"         : data.mikan_id,
            "img_url"          : data.img_url,
            "update_day"       : data.update_day,
            "anime_type"       : data.anime_type,
            "subscribe_status" : data.subscribe_status,
        }
        list.append(dic)
    return list

def query_anime_seed_by_condition(mikan_id=-1, subgroup_id=-1, episode=-1, seed_name='', seed_url='', seed_status=-1, seed_size=''):
    log_info_str = "[MODELS] query_anime_seed_by_condition,"
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if subgroup_id != -1:
        log_info_str += " subgroup_id: {},".format(subgroup_id)
    if episode != -1:
        log_info_str += " episode: {},".format(episode)
    if seed_name != '':
        log_info_str += " seed_name: {},".format(seed_name)
    if seed_url != '':
        log_info_str += " seed_url: {},".format(seed_url)
    if seed_status != -1:
        log_info_str += " seed_status: {},".format(seed_status)
    if seed_size != '':
        log_info_str += " seed_size: {},".format(seed_size)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeSeed)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if subgroup_id != -1:
        session = session.filter_by(subgroup_id=subgroup_id)
    if episode != -1:
        session = session.filter_by(episode=episode)
    if seed_name != '':
        session = session.filter_by(seed_name=seed_name)
    if seed_url != '':
        session = session.filter_by(seed_url=seed_url)
    if seed_status != -1:
        session = session.filter_by(seed_status=seed_status)
    if seed_size != '':
        session = session.filter_by(seed_size=seed_size)
    result = session.all()
    list = []
    for data in result:
        dic = {
            "index"       : data.index,
            "mikan_id"    : data.mikan_id,
            "subgroup_id" : data.subgroup_id,
            "episode"     : data.episode,
            "seed_name"   : data.seed_name,
            "seed_url"    : data.seed_url,
            "seed_status" : data.seed_status,
            "seed_size"   : data.seed_size
        }
        list.append(dic)
    return list

def query_anime_task_by_condition(mikan_id=-1, episode=-1, torrent_name='', qb_task_status=-1):
    log_info_str = "[MODELS] query_anime_task_by_condition,"
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if episode != -1:
        log_info_str += " episode: {},".format(episode)
    if torrent_name != '':
        log_info_str += " torrent_name: {},".format(torrent_name)
    if qb_task_status != -1:
        log_info_str += " qb_task_status: {},".format(qb_task_status)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeTask)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if episode != -1:
        session = session.filter_by(episode=episode)
    if torrent_name != '':
        session = session.filter_by(torrent_name=torrent_name)
    if qb_task_status != -1:
        session = session.filter_by(qb_task_status=qb_task_status)
    result = session.all()
    list = []
    for data in result:
        dic = {
            "index"          : data.index,
            "mikan_id"       : data.mikan_id,
            "episode"        : data.episode,
            "torrent_name"   : data.torrent_name,
            "qb_task_status" : data.qb_task_status,
        }
        list.append(dic)
    return list

def query_anime_broadcast_by_condition(mikan_id=-1, year=-1, season=-1):
    log_info_str = "[MODELS] query_anime_broadcast_by_condition,"
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if year != -1:
        log_info_str += " year: {},".format(year)
    if season != -1:
        log_info_str += " season: {},".format(season)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeBroadcast)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if year != -1:
        session = session.filter_by(year=year)
    if season != -1:
        session = session.filter_by(season=season)
    result = session.all()
    list = []
    for data in result:
        dic = {
            "index"    : data.index,
            "mikan_id" : data.mikan_id,
            "year"     : data.year,
            "season"   : data.season
        }
        list.append(dic)
    return list

def query_anime_subgroup_by_condition(subgroup_id=-1, subgroup_name=''):
    log_info_str = "[MODELS] query_anime_subgroup_by_condition,"
    if subgroup_id != -1:
        log_info_str += " subgroup_id: {},".format(subgroup_id)
    if subgroup_name != '':
        log_info_str += " subgroup_name: {},".format(subgroup_name)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeSubgroup)
    if subgroup_id != -1:
        session = session.filter_by(subgroup_id=subgroup_id)
    if subgroup_name != '':
        session = session.filter_by(subgroup_name=subgroup_name)
    result = session.all()
    list = []
    for data in result:
        dic = {
            "index"         : data.index,
            "subgroup_id"   : data.subgroup_id,
            "subgroup_name" : data.subgroup_name,
        }
        list.append(dic)
    return list

def delete_anime_list_by_condition(anime_name='', mikan_id=-1, img_url= '', update_day=-1, anime_type=-1, subscribe_status=-1):
    log_info_str = "[MODELS] delete_anime_list_by_condition,"
    if anime_name != '':
        log_info_str += " anime_name: {},".format(anime_name)
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if img_url != '':
        log_info_str += " img_url: {},".format(img_url)
    if update_day != -1:
        log_info_str += " update_day: {},".format(update_day)
    if anime_type != -1:
        log_info_str += " anime_type: {},".format(anime_type)
    if subscribe_status != -1:
        log_info_str += " subscribe_status: {},".format(subscribe_status)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeList)
    if anime_name != '':
        session = session.filter_by(anime_name=anime_name)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if img_url != '':
        session = session.filter_by(img_url=img_url)
    if update_day != -1:
        session = session.filter_by(update_day=update_day)
    if anime_type != -1:
        session = session.filter_by(anime_type=anime_type)
    if subscribe_status != -1:
        session = session.filter_by(subscribe_status=subscribe_status)
    query = session.all()
    count = 0
    for data in query:
        db.session.delete(data)
        count = count + 1
    if count > 0:
        return session_commit()
    return False

def delete_anime_seed_by_condition(mikan_id=-1, subgroup_id=-1, episode=-1, seed_name='', seed_url='', seed_status=-1, seed_size=''):
    log_info_str = "[MODELS] delete_anime_seed_by_condition,"
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if subgroup_id != -1:
        log_info_str += " subgroup_id: {},".format(subgroup_id)
    if episode != -1:
        log_info_str += " episode: {},".format(episode)
    if seed_name != '':
        log_info_str += " seed_name: {},".format(seed_name)
    if seed_url != '':
        log_info_str += " seed_url: {},".format(seed_url)
    if seed_status != -1:
        log_info_str += " seed_status: {},".format(seed_status)
    if seed_size != '':
        log_info_str += " seed_size: {},".format(seed_size)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeSeed)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if subgroup_id != -1:
        session = session.filter_by(subgroup_id=subgroup_id)
    if episode != -1:
        session = session.filter_by(episode=episode)
    if seed_name != '':
        session = session.filter_by(seed_name=seed_name)
    if seed_url != '':
        session = session.filter_by(seed_url=seed_url)
    if seed_status != -1:
        session = session.filter_by(seed_status=seed_status)
    if seed_size != '':
        session = session.filter_by(seed_size=seed_size)
    query = session.all()
    count = 0
    for data in query:
        db.session.delete(data)
        count = count + 1
    if count > 0:
        return session_commit()
    return False

def delete_anime_task_by_condition(mikan_id=-1, qb_task_status=-1, episode=-1, torrent_name=''):
    log_info_str = "[MODELS] delete_anime_task_by_condition,"
    if mikan_id != -1:
        log_info_str += " mikan_id: {},".format(mikan_id)
    if qb_task_status != -1:
        log_info_str += " qb_task_status: {},".format(qb_task_status)
    if episode != -1:
        log_info_str += " episode: {},".format(episode)
    if torrent_name != '':
        log_info_str += " torrent_name: {},".format(torrent_name)
    logger.info(log_info_str[:-1])

    session = db.session.query(AnimeTask)
    if mikan_id != -1:
        session = session.filter_by(mikan_id=mikan_id)
    if qb_task_status != -1:
        session = session.filter_by(qb_task_status=qb_task_status)
    if episode != -1:
        session = session.filter_by(episode=episode)
    if torrent_name != '':
        session = session.filter_by(torrent_name=torrent_name)
    query = session.all()
    count = 0
    for data in query:
        db.session.delete(data)
        count = count + 1
    if count > 0:
        return session_commit()
    return False

def update_anime_list_subscribe_status_by_mikan_id(mikan_id, subscribe_status):
    logger.info("[MODELS] update_anime_list_subscribe_status_by_mikan_id, mikan_id: {}, subscribe_status: {}".format(mikan_id, subscribe_status))

    db.session.query(AnimeList).filter_by(mikan_id=mikan_id).update({"subscribe_status": subscribe_status})
    return session_commit()

def update_anime_seed_seed_status_by_seed_url(seed_url, seed_status):
    logger.info("[MODELS] update_anime_seed_seed_status_by_seed_url, seed_url: {}, seed_status: {}".format(seed_url, seed_status))

    db.session.query(AnimeSeed).filter_by(seed_url=seed_url).update({"seed_status": seed_status})
    return session_commit()

def update_anime_task_qb_task_status_by_torrent_name(torrent_hash, qb_task_status):
    logger.info("[MODELS] update_anime_task_qb_task_status_by_torrent_name, torrent_name: {}, qb_task_status: {}".format(torrent_hash, qb_task_status))

    torrent_hash_string = "%" + torrent_hash + "%"
    db.session.query(AnimeTask).filter(AnimeTask.torrent_name.like(torrent_hash_string)).update({"qb_task_status": qb_task_status})
    return session_commit()