import os, json, subprocess, sys
import maya.cmds as cmds
import maya.utils as utils
from functools import partial
import maya.mel as mel
import pymel.core as pm

# path to custom scripts
sys.path.append(r'/Users/johan/Dev/maya/petfactory_maya_scripts')
sys.path.append(r'/Users/johan/Documents/assets/maya/scripts')

# path to the maya prefs scripts dir
script_path = r'/Users/johan/Library/Preferences/Autodesk/maya/2015-x64/scripts/'

parent_menu_name = 'Petfactory'


#import petfactory.marking_menu.marking_menu as petfactory_mm


def pet_init():
    build_petfactory_menu()

def read_json(file_path):

    if os.path.exists(file_path):
        
        f = open(file_path,'r')
        data = f.read()
        f.close()
        
        try:
            ret_dict = json.loads(data)
            return ret_dict

        except ValueError as e:
            print('Error reading json:\n{0}'.format(e))

    else:
        print('file does not exist:\n{0}'.format(file_path))

    print('Reach en of read_json')
    return None


def open_dir(dir_name, absolute_path, *args):
    
    '''
    Open the specified dir specified by the dir_name param.
    If param absolute_path is true the dir_name will be used as an absolute path.
    '''

    if absolute_path:
        folder_path = dir_name

    else:
        proj_dir = cmds.workspace(q=True, fn=True)
        folder_path = os.path.join(proj_dir, dir_name)
    
    if not os.path.exists(folder_path):
        cmds.confirmDialog(t='Could not find directory', b=['OK'],m='The directory does not exist:\n {0}'.format(folder_path))
    
    else:
        # try to open the directory
        try:
            subprocess.check_call(['open', '--', folder_path])
        
        except:
            cmds.confirmDialog(t='Error', b=['OK'],m='Unable to open folder:\n{0}'.format(folder_path))


def build_petfactory_menu():

    if cmds.menu('petfactory_menu', exists=1):
        cmds.deleteUI('petfactory_menu')

    # add to the main menu
    root_menu = cmds.menu('petfactory_menu', p='MayaWindow', to=1, aob=1, l=parent_menu_name)

    # the quick open folder menu
    proj_dir_menuitem = cmds.menuItem('open_proj_dir', p=root_menu, bld=1, sm=1, to=1, l='Open Project Directory')

    cmds.menuItem('movies', parent=proj_dir_menuitem, c=partial(open_dir, 'movies', False), label='movies')
    cmds.menuItem('sourceimages', parent=proj_dir_menuitem, c=partial(open_dir, 'sourceimages', False), label='sourceimages')
    cmds.menuItem('images', parent=proj_dir_menuitem, c=partial(open_dir, 'images', False), label='images')
    cmds.menuItem('scenes', parent=proj_dir_menuitem, c=partial(open_dir, 'scenes', False), label='scenes')
    cmds.menuItem(p=proj_dir_menuitem, d=1)
    cmds.menuItem('scripts', parent=proj_dir_menuitem, c=partial(open_dir, script_path, True), label='scripts')

    cmds.menuItem(p=root_menu, d=1)

    script_dict = read_json(os.path.join(script_path, 'script_config.json'))
    
    # add the custom scripts
    if script_dict:

        petfactory_custom_script_menu(script_dict, root_menu)

def petfactory_custom_script_menu(json_dict, parent_menu):

    main_script_dict = json_dict.get('scripts')
    
    category_keys = main_script_dict.keys()
    category_keys.sort()
    
    for category in category_keys:
    
        category_script_dict = main_script_dict[category]
        category_script_keys = category_script_dict.keys()
        category_script_keys.sort()
    
        script_menuitem = cmds.menuItem(category, p=parent_menu, bld=1, sm=1, to=1, l=category)  
    
        for category_script in category_script_keys:
    
            script_info_dict = category_script_dict[category_script]
            
            filename = script_info_dict.get('filename')
            ext = script_info_dict.get('ext')
            cmd = script_info_dict.get('cmd')
    
            if filename is None:
                print('"filename" missing from {0}.{1}, continue...'.format(category, filename))
                continue
            if ext is None:
                print('"ext" missing from {0}.{1}, continue...'.format(category, filename))
                continue
            elif cmd is None:
                print('"cmd" missing from {0}.{1}, continue...'.format(category, filename))
                continue
            
            # check if we have specified a sub dir (relative to the category dir)
            rel_path = script_info_dict.get('rel_path')
            
            if rel_path:
                module = 'petfactory.{0}.{1}.{2}'.format(category, rel_path, filename)
            else:
                module = 'petfactory.{0}.{1}'.format(category, filename)
            
            # construct the button press cmd
            cmd_string = 'try:\n\texec "import {0}"\n\nexcept ImportError as e:\n\tprint "import error:", e\n'.format(module)
            cmd_string += '\n{0}.{1}()'.format(module, cmd)
            
            cmds.menuItem(category_script, parent=script_menuitem, c=cmd_string, label=category_script)
'''           
def petfactory_custom_script_menu(script_dict, parent_menu):

    print('Called: petfactory_custom_script_menu')

    category_dict = script_dict.get('scripts')

    for category in sorted(category_dict):

        script_menuitem = cmds.menuItem(category, p=parent_menu, bld=1, sm=1, to=1, l=category)            
        script_dict = category_dict[category]

        for script in sorted(script_dict):

            # build the string to be used for the menuItem button command.
            # the script is imported when the menu item is pressed,
            # the the cmd specified in the info_dict is called.

            rel_path = script_dict[script].get('rel_path')
            if rel_path:
                module = 'petfactory.{0}.{1}.{2}'.format(category, rel_path, script)
            else:
                module = 'petfactory.{0}.{1}'.format(category, script)
            
            cmd = 'try:\n\texec "import {0}"\n\nexcept ImportError as e:\n\tprint "import error:", e\n'.format(module)
            cmd += '\n{0}.{1}()'.format(module, script_dict[script].get('cmd'))
            
            cmds.menuItem(script, parent=script_menuitem, c=cmd, label=script)
'''
utils.executeDeferred('pet_init()')