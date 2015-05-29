from django.db import models

class InetnumModel(models.Model):
    inet = models.GenericIPAddressField()
    init_ip = models.GenericIPAddressField(editable=False, blank=True, null=True)
    end_ip = models.GenericIPAddressField(editable=False, blank=True, null=True)
    prefix_length = models.PositiveSmallIntegerField(editable=False, blank=True, null=True)
    
    @staticmethod
    def int_to_ipstr(ip, ip_size):
        import socket
        import binascii
        
        hex_ip = hex(ip)[2:]
        if hex_ip[-1] == 'L':
            hex_ip = hex_ip[:-1]

        if len(hex_ip) != (ip_size / 4):
            zeros = (ip_size / 4) - len(hex_ip)
            hex_ip = ('0' * zeros) + hex_ip
        
        if ip_size == 32:
            hex_ip = binascii.unhexlify(hex_ip)
            return socket.inet_ntop(socket.AF_INET, hex_ip)
        elif ip_size == 128:
            hex_ip = binascii.unhexlify(hex_ip)
            return socket.inet_ntop(socket.AF_INET6, hex_ip)
        else:
            raise ValueError('Unrecognized IP size: %r' % ip_size)

    @staticmethod
    def ipstr_to_int(ip):
        import socket
        import binascii
        
        int_ip = 0
        ip_size = 0
        try:
            int_ip = socket.inet_pton(socket.AF_INET, ip)
            ip_size = 32
        except:
            try:
                int_ip = socket.inet_pton(socket.AF_INET6, ip)
                ip_size = 128
            except:
                int_ip = -1
                ip_size = -1
        
        if int_ip == -1:
            return None
                    
        int_ip = int(binascii.hexlify(int_ip), 16)
        
        return (int_ip, ip_size)
        
    @staticmethod
    def split_inet(inet):
        splitted_inet = inet.split('/')
        
        prefix = None
        if len(splitted_inet) == 2:
            prefix = int(splitted_inet[1])
            
        (ip_int, ip_size) = InetnumModel.ipstr_to_int(splitted_inet[0])

        return (ip_int, ip_size, prefix)
        
    @staticmethod
    def inet_borders(inet):
        (ip_int, ip_size, prefix) = InetnumModel.split_inet(inet)
        imask = ('1' * prefix) + ('0' * (ip_size - prefix))
        init_ip = InetnumModel.int_to_ipstr(int(imask, 2) & ip_int, ip_size)
        emask = ('0' * prefix) + ('1' * (ip_size - prefix))
        end_ip = InetnumModel.int_to_ipstr(int(emask, 2) | ip_int, ip_size)
        
        return (init_ip, end_ip)

    def _update_inet_borders(self):
        (init_ip, end_ip) = InetnumModel.inet_borders(self.inet)
        self.init_ip = init_ip
        self.end_ip = end_ip
        
    def _update_prefix(self):
        (ip_int, ip_size, prefix) = InetnumModel.split_inet(self.inet)
        self.prefix_length = str(prefix)
    
    def save(self, *args, **kwargs):
        self._update_inet_borders()
        self._update_prefix()
        
        super(InetnumModel, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.inet)
        
    class Meta:
        abstract = True
        ordering = ['prefix_length', ]
