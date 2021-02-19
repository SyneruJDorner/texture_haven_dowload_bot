import sys, os, time, shutil, subprocess, json
import selenium_helper as selenium
from pyunpack import Archive
import requests
from progress.bar import Bar
from PIL import Image
from configparser import ConfigParser
import icon_lib


def get_json_data():
    with open('config.json') as json_file:
        data = json.load(json_file)
    return data


def download_wait(directory, timeout=1440, nfiles=None):
    seconds = 0
    dl_wait = True

    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)

        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        if (dl_wait == False):
            break
        seconds += 1
    return seconds


def getFolderSize(p):
   from functools import partial
   prepend = partial(os.path.join, p)
   return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])


def get_folder_path(child_name, folder_contents):
    save_path = get_json_data()['texture_save_path']
    folder_path = []

    if (folder_contents == "jpg"):
        folder_contents = "JPEG"
    elif (folder_contents == "png"):
        folder_contents = "PNG"
    else:
        raise Exception("Invalid folder_contents provided, it should be 'jpg' or 'png'")


    folder_path = [save_path + child_name + "\\" + folder_contents + "\\1k",
            save_path + child_name + "\\" + folder_contents + "\\2k",
            save_path + child_name + "\\" + folder_contents + "\\4k",
            save_path + child_name + "\\" + folder_contents + "\\8k"]

    if (child_name == "brick_4" or child_name == "brown_brick_02"):
        folder_path = [save_path + child_name + "\\" + folder_contents + "\\1k",
                    save_path + child_name + "\\" + folder_contents + "\\2k",
                    save_path + child_name + "\\" + folder_contents + "\\4k",
                    save_path + child_name + "\\" + folder_contents + "\\7k"]

    return folder_path


def create_jpeg_paths(child_name):
    path_JPEG = get_folder_path(child_name=child_name, folder_contents="jpg")

    try:
        for path in path_JPEG:
            os.makedirs(path)
    except OSError:
        pass
    else:
        pass
    return path_JPEG


def create_png_paths(child_name):
    path_PNG = get_folder_path(child_name=child_name, folder_contents="png")

    try:
        for path in path_PNG:
            os.makedirs(path)
    except OSError:
        pass
    else:
        pass
    return path_PNG


def get_download_links(child_name, download_type):
    download_links = []

    if (download_type == "jpg"):
        pass
    elif (download_type == "png"):
        pass
    else:
        raise Exception("Invalid download_type provided, it should be 'jpg' or 'png'")

    download_links = ["https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("1k", child_name, child_name, "1k", download_type),
                    "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("2k", child_name, child_name, "2k", download_type),
                    "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("4k", child_name, child_name, "4k", download_type),
                    "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("8k", child_name, child_name, "8k", download_type)]

    if (child_name == "brick_4" or child_name == "brown_brick_02"):
        download_links = ["https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("1k", child_name, child_name, "1k", download_type),
                            "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("2k", child_name, child_name, "2k", download_type),
                            "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("4k", child_name, child_name, "4k", download_type),
                            "https://texturehaven.com/files/textures/zip/{0}/{1}/{2}_{3}_{4}.zip".format("7k", child_name, child_name, "7k", download_type)]

    return download_links


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')


def download_JPEG_files(driver, child_name, path_JPEG, debug=False):
    if (debug == True):
        print(child_name, path_JPEG)

    download_links = get_download_links(child_name, "jpg")
    download_path = get_download_path()

    for i, path in enumerate(path_JPEG, start=0):
        if (getFolderSize(path) > 0):
            continue
    
        driver.get(download_links[i])
        download_wait(download_path)
        file_name = download_links[i].replace("https://texturehaven.com/files/textures/zip/", "")
        file_name = file_name[file_name.rindex('/')+1:]
        Archive(download_path + "\\" + file_name).extractall(path)
        os.remove(download_path + "\\" + file_name)
        pass
    return


def download_PNG_files(driver, child_name, path_PNG, debug=False):
    if (debug == True):
        print(child_name, path_PNG)

    download_links = get_download_links(child_name, "png")
    download_path = get_download_path()

    for i, path in enumerate(path_PNG, start=0):
        if (getFolderSize(path) > 0):
            continue
        
        driver.get(download_links[i])
        download_wait(download_path)
        file_name = download_links[i].replace("https://texturehaven.com/files/textures/zip/", "")
        file_name = file_name[file_name.rindex('/')+1:]
        Archive(download_path + "\\" + file_name).extractall(path)
        os.remove(download_path + "\\" + file_name)
        pass
    return


def download_icon_file(driver, icon_src, child_name):
    save_path = get_json_data()['texture_save_path']

    jpg_path = save_path + child_name + "\\" + 'Title.jpg'
    ico_path = save_path + child_name + "\\" + 'Title.ico'

    if (os.path.isfile(ico_path) == False):
        img = requests.get("https://texturehaven.com" +  icon_src)
        with open(jpg_path, 'wb') as writer:
            writer.write(img.content)

        image = Image.open(jpg_path)
        MAX_SIZE = 256, 256
        image.thumbnail(MAX_SIZE)
        image.save(ico_path)
        os.remove(jpg_path)
        subprocess.check_call(["attrib","+H", ico_path])

        icon_lib.SetFolderIcon(save_path + child_name, ico_path, True)


def main(argv):
    driver, wait = selenium.init(get_json_data()['driver_path'])
    driver.get("https://texturehaven.com/textures/?o=date_published")

    grid_items_xpath = '/html/body/div/div[3]/div[3]/div[2]'
    grid_items_element = wait.until(selenium.EC.presence_of_element_located((selenium.By.XPATH, grid_items_xpath)))
    child_elements = grid_items_element.find_elements(selenium.By.XPATH, ".//a")
    bar = Bar('Downloading', fill='█', suffix='%(percent)d%%', max=len(child_elements))
    for child in child_elements:
        bar.next()
        child_name = child.find_element(selenium.By.XPATH, ".//div/div[2]/div/div/h3").get_attribute('innerText')
        icon_src = child.find_element(selenium.By.XPATH, ".//div/div[1]/img[2]").get_attribute("data-src")

        path_JPEG = create_jpeg_paths(child_name)
        path_PNG = create_png_paths(child_name)

        download_JPEG_files(driver=driver, child_name=child_name, path_JPEG=path_JPEG, debug=False)
        download_PNG_files(driver=driver, child_name=child_name, path_PNG=path_PNG, debug=False)
        download_icon_file(driver, icon_src, child_name)

    bar.finish()
    print("Completed! Shutting down")
    driver.close()
    driver.quit()
    return


if __name__ == "__main__":
    main(sys.argv)