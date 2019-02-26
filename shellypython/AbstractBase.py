class AbstractBase(object):
    def to_dictionary(self):
        result = {}
        for k,  v in self.__dict__.items():
            if k.startswith('__'):
                continue
            if isinstance(v, AbstractBase):
                result[v.__class__.__name__] = (v.to_dictionary())
            else:
                result[k] = v
        return result
