import collections
import threading

from sqlalchemy import Column, UnicodeText, Boolean, Integer

from tg_bot.modules.sql import BASE, SESSION


class AFK(BASE):
    __tablename__ = "afk_users"

    user_id = Column(Integer, primary_key=True)
    is_afk = Column(Boolean)
    reason = Column(UnicodeText)

    def __init__(self, user_id, reason="", is_afk=True):
        self.user_id = user_id
        self.reason = reason
        self.is_afk = is_afk

    def __repr__(self):
        return "afk_status for {}".format(self.user_id)


AFK.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.Lock()
KEYSTORE = collections.defaultdict(list)


# check if need insertion lock
def check_afk_status(user_id):
    return SESSION.query(AFK).get(user_id)


def set_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if not curr:
            curr = AFK(user_id, reason, True)
        else:
            curr.is_afk = True
        SESSION.add(curr)
        SESSION.commit()


def rm_afk(user_id):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if curr:
            SESSION.delete(curr)
            SESSION.commit()
            return True
        return False


def toggle_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if not curr:
            curr = AFK(user_id, reason, True)
        elif curr.is_afk:
            curr.is_afk = False
        elif not curr.is_afk:
            curr.is_afk = True
        SESSION.add(curr)
        SESSION.commit()


def load_keystore():
    with INSERTION_LOCK:
        all_users = SESSION.query(AFK).all()
        for user in all_users:
            KEYSTORE[user.user_id].append(user)
        SESSION.close()
        print("{} total afk users added to {} chats.".format(len(all_users), len(KEYSTORE)))


load_keystore()
