# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# json_tools - JSON load and parse functions with library detection
# --------------------------------------------------------------------------------

import traceback

from platformcode import logger
from inspect import stack

try:
    import json
except:
    logger.info("json included in the interpreter **NOT** available")

    try:
        import simplejson as json
    except:
        logger.info("simplejson included in the interpreter **NOT** available")
        try:
            from lib import simplejson as json
        except:
            logger.info("simplejson in lib directory **NOT** available")
            logger.error("A valid JSON parser was not found")
            json = None
        else:
            logger.info("Using simplejson in the lib directory")
    else:
        logger.info("Using simplejson included in the interpreter")
# ~ else:
    # ~ logger.info("Usando json incluido en el interprete")

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


def load(*args, **kwargs):
    if "object_hook" not in kwargs:
        kwargs["object_hook"] = to_utf8

    try:
        value = json.loads(*args, **kwargs)
    except:
        logger.error("**NOT** able to load the JSON")
        logger.error(traceback.format_exc())
        logger.error('ERROR STACK ' + str(stack()[1][3]))
        value = {}

    return value


def dump(*args, **kwargs):
    if not kwargs:
        kwargs = {"indent": 4, "skipkeys": True, "sort_keys": True, "ensure_ascii": True}

    try:
        value = json.dumps(*args, **kwargs)
    except:
        logger.error("JSON could **NOT** be saved")
        logger.error(traceback.format_exc())
        value = ""
    return value


def to_utf8(dct):
    if isinstance(dct, dict):
        return dict((to_utf8(key), to_utf8(value)) for key, value in dct.items())
    elif isinstance(dct, list):
        return [to_utf8(element) for element in dct]
    elif isinstance(dct, unicode):
        dct = dct.encode("utf8")
        if PY3: dct = dct.decode("utf8")
        return dct
    elif PY3 and isinstance(dct, bytes):
        return dct.decode('utf-8')
    else:
        return dct


def get_node_from_file(name_file, node, path=None):
    """
    Obtiene el nodo de un fichero JSON

    @param name_file: Puede ser el nombre de un canal o server (sin incluir extension)
     o bien el nombre de un archivo json (con extension)
    @type name_file: str
    @param node: nombre del nodo a obtener
    @type node: str
    @param path: Ruta base del archivo json. Por defecto la ruta de settings_channels.
    @return: dict con el nodo a devolver
    @rtype: dict
    """
    logger.info()
    from platformcode import config
    from core import filetools

    dict_node = {}

    if not name_file.endswith(".json"):
        name_file += "_data.json"

    if not path:
        path = filetools.join(config.get_data_path(), "settings_channels")

    fname = filetools.join(path, name_file)

    if filetools.isfile(fname):
        data = filetools.read(fname)
        dict_data = load(data)

        check_to_backup(data, fname, dict_data)

        if node in dict_data:
            dict_node = dict_data[node]

    #logger.debug("dict_node: %s" % dict_node)

    return dict_node


def check_to_backup(data, fname, dict_data):
    """
    Comprueba que si dict_data(conversion del fichero JSON a dict) no es un diccionario, se genere un fichero con
    data de nombre fname.bk.

    @param data: contenido del fichero fname
    @type data: str
    @param fname: nombre del fichero leido
    @type fname: str
    @param dict_data: nombre del diccionario
    @type dict_data: dict
    """
    logger.info()

    if not dict_data:
        logger.error("Error loading json from file %s" % fname)

        if data != "":
            # se crea un nuevo fichero
            from core import filetools
            title = filetools.write("%s.bk" % fname, data)
            if title != "":
                logger.error("There was an error saving the file: %s.bk" % fname)
            else:
                logger.debug("A copy with the name has been saved: %s.bk" % fname)
        else:
            logger.debug("The file is empty: %s" % fname)


def update_node(dict_node, name_file, node, path=None, silent=False):
    """
    actualiza el json_data de un fichero con el diccionario pasado

    @param dict_node: diccionario con el nodo
    @type dict_node: dict
    @param name_file: Puede ser el nombre de un canal o server (sin incluir extension)
     o bien el nombre de un archivo json (con extension)
    @type name_file: str
    @param node: nodo a actualizar
    @param path: Ruta base del archivo json. Por defecto la ruta de settings_channels.
    @return result: Devuelve True si se ha escrito correctamente o False si ha dado un error
    @rtype: bool
    @return json_data
    @rtype: dict
    """
    if not silent: logger.info()

    from platformcode import config
    from core import filetools
    json_data = {}
    result = False

    if not name_file.endswith(".json"):
        name_file += "_data.json"

    if not path:
        path = filetools.join(config.get_data_path(), "settings_channels")

    fname = filetools.join(path, name_file)

    try:
        data = filetools.read(fname)
        dict_data = load(data)
        # es un dict
        if dict_data:
            if node in dict_data:
                if not silent: logger.debug("   the key exists %s" % node)
                dict_data[node] = dict_node
            else:
                if not silent: logger.debug("   The key does NOT exist %s" % node)
                new_dict = {node: dict_node}
                dict_data.update(new_dict)
        else:
            if not silent: logger.debug("   It is NOT a dict")
            dict_data = {node: dict_node}
        json_data = dump(dict_data)
        result = filetools.write(fname, json_data)
    except:
        logger.error("Could not update %s" % fname)

    return result, json_data
