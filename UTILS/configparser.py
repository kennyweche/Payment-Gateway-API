import os
import ConfigParser

class Cparser:

    @staticmethod
    def get_em_configs(app_config_rel_path=None,section=None):
       try:
          if app_config_rel_path is None:
             app_config_rel_path='CONFIG/configs.ini'
          current_dir=os.path.dirname(os.path.realpath(__FILE__))
          config_file=os.path.join(current_dir,'../{0}'.format(app_config_rel_path))
          cparser = ConfigParser.ConfigParser()
          cparser.read(config_file)
          section = section or "DB"
          options=cparser.options(section)
          config_dict={}
          for option in options:
              try:
                 config_dict[option]=cparser.get(section, option)
                 if config_dict[option] == -1:
                     print "Invalid configs parsed {0}{1}".format(section, option)
              except Exception,e:
                 print "Parse exception {0}".format(e)
          return config_dict
       except Exception,e:
           print "Ni blunder kuparse iyo file joh!. Noma ni {0}".format(e) 
