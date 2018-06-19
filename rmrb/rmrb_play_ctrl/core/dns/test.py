
import resolver

resObj = resolver.Resolver()


from rmrb_play_ctrl.core.dns import resolver

resObj = resolver.Resolver()
resObj.nameservers = ['8.8.8.8']
stra = resObj.query('pricloud.cn', 'a')
print 'result:', stra

