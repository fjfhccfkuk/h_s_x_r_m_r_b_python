#/usr/bin/python


class media_listener(object):
    def media_updated(self, m_list):
        raise  Exception("this func should override by subclass")

    def media_changed(self):
        raise Exception("this func should override by subclass")

    def win_time_changed(self, t_show, t_hide):
        raise Exception("this func should override by subclass")
