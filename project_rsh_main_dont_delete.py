import random
import time
import json
import os
import c4d
from c4d import gui

# ОДНО ИМЯ КЛАССА ДЛЯ МОДЕЛЕК
CLASS_NAME = "Aristocracy"


# НАЧАЛЬНЫЙ НОМЕР
START_VALUE = 1


# ПУТЬ К ФАЙЛУ С НОМЕРАМИ
PATH_TO_NUMBERS = r"G:\Work\ANIME\main\render\test\USED_NUMBERS.txt".encode("utf-8")
# путь добавить внутрь кавычек, например: r"C:\Users\user\Desktop\test.txt".encode("utf-8")
# если файл не существует, то он будет создан автоматически
# можно использовать как \, так и /

# ПЕРВЫЙ ФАЙЛ, В КОТОРЫЙ ЗАПИСЫВАЮТСЯ ИСКЛЮЧЕНИЯ
# пример был под названием "x.txt"
PATH_TO_EXCEPTION_FILE = r"~/Desktop/x.txt".encode("utf-8")

# ВТОРОЙ ФАЙЛ, В КОТОРЫЙ ЗАПИСЫВАЮТСЯ ОГРАНИЧЕНИЯ
# пример был под названием "x2.txt"
PATH_TO_COUNT_FILE = r"~/Desktop/x2.txt".encode("utf-8")

# волосы и хедгеары конфликтуют? если да, то раскоментировать нужный вариант, другой закоментировать
# для того, чтобы закоментировать строку, нужно поставить перед ней знак #
# и наоборот, чтобы раскоментировать строку, нужно убрать перед ней знак #
HEADGEAR_CONFLICT = False
# HEADGEAR_CONFLICT = True



COUNT = int(c4d.gui.InputDialog("How many models do you need?"))

SEED = 12345
prompt_seed = c4d.gui.InputDialog("Input seed or input 0 or close dialog for default")
if prompt_seed != "" and int(prompt_seed) != 0:
    SEED = prompt_seed
random.seed(SEED)




pwd_png = c4d.storage.LoadDialog(
    title="Folder for .png", flags=c4d.FILESELECT_DIRECTORY
)
pwd_json = c4d.storage.LoadDialog(
    title="Folder for .json", flags=c4d.FILESELECT_DIRECTORY
)


count_copy = COUNT


if not os.path.exists(PATH_TO_NUMBERS):
    with open(PATH_TO_NUMBERS, "w", encoding="utf-8") as f:
        f.write("")

with open(PATH_TO_NUMBERS, "r", encoding="utf-8") as f:
    vals = f.readline()
    while "  " in vals:
        vals = vals.replace("  ", " ")
    vals.strip()
    already_used_vals = set(map(int, vals.split()))

current_using_vals = list()


# Код генерирует список из рандомных значений и добавляет также в set
while len(current_using_vals) < COUNT:
    random_val = random.randint(int(START_VALUE), 10_000)
    if random_val not in already_used_vals:
        current_using_vals.append(random_val)
        already_used_vals.add(random_val)


nfts: list[dict | None] = []
pre_count = 0
forb_list = []
if PATH_TO_EXCEPTION_FILE is not None:
    with open(PATH_TO_EXCEPTION_FILE, "r", encoding="utf-8") as f:
        x = f.readlines()
        for i in x:
            i = i.strip()
            forb_list.append(tuple(i.split()))

if not pwd_png or not pwd_json:
    exit(1)

restricts = []

if PATH_TO_COUNT_FILE is not None:
    with open(PATH_TO_COUNT_FILE, "r", encoding="utf-8") as f:
        x = f.readlines()
        for i in x:
            i = i.strip()
            i = i.split()
            if len(i) < 3:
                continue
            pre_count += int(i[2])
            restricts.append([i[0], i[1], int(i[2])])


pwd_png += "\\"
pwd_json += "\\"


def used_numbers_dumping(path_to_file=PATH_TO_NUMBERS):
    """Dumping used numbers to file"""
    with open(path_to_file, "w", encoding="utf-8") as f:
        global already_used_vals
        already_used_vals = list(already_used_vals)
        RESULT = " ".join(map(str, already_used_vals))
        f.write(RESULT)


def nft_names_saving():
    """Saving nft names to json"""
    global nfts
    for i in nfts:
        current_val = list(i.keys())[0]
        with open(f"{pwd_json}{current_val}.json", "w", encoding="utf-8") as f:
            json.dump(i[current_val], f, indent=4)

    # for i, nft_dict in enumerate(nfts):
    #     file_number = list(nft_dict.keys())[0]
    #     saving_val = nft_dict[file_number]
    #     NUMBER = saving_val["NUMBER"]
    #     del saving_val["NUMBER"]

    #     with open(f"{pwd_json}{NUMBER}.json", "w", encoding="utf-8") as f:
    #         json.dump(saving_val, f, indent=4)
    nft = dict()
    nft["nft"] = nfts
    with open(pwd_json + "all_info.json", "w", encoding="utf-8") as f:
        json.dump(nft, f, indent=4)


used_numbers_dumping(PATH_TO_NUMBERS + r".temp".encode("utf-8"))


def render(name):
    """
    Рендерит текущий документ с использованием заданного имени и сохраняет вывод в виде файла PNG.

    Args:
        name (str): Имя, которое будет использоваться для вывода рендера.

    Errors:
        RuntimeError: Если произошла ошибка во время рендеринга или сохранения вывода.
    """
    global count_copy
    print(f"Left: {count_copy}\n\n")
    if count_copy <= 0:
        return

    count_copy -= 1
    c4d.StatusSetText("Rendering " + name)
    # Retrieves a copy of the current documents render settings
    rd = doc.GetActiveRenderData().GetClone().GetData()
    if rd is None:
        raise RuntimeError(
            "Failed to retrieve the clone of the active Render Settings."
        )

    # Sets various render parameters
    rd[c4d.RDATA_SAVEIMAGE] = False

    # Gets the x and y res from the render settings
    xRes = int(rd[c4d.RDATA_XRES])
    yRes = int(rd[c4d.RDATA_YRES])

    # Initializes the bitmap with the result size
    # The resolution must match with the output size of the render settings
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise RuntimeError("Failed to create the Bitmap.")

    if bmp.Init(x=xRes, y=yRes) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to initialize the Bitmap.")

    # Calls the renderer
    res = c4d.documents.RenderDocument(
        doc, rd, bmp, c4d.RENDERFLAGS_CREATE_PICTUREVIEWER
    )

    # Leaves if there is an error while rendering
    if res != c4d.RENDERRESULT_OK:
        raise RuntimeError("Failed to render the document.")

    # Displays the bitmap in the Picture Viewer
    bmp.Save(pwd_png + str(current_using_vals[-count_copy]) + ".png", c4d.FILTER_PNG)
    # c4d.bitmaps.ShowBitmap(bmp)


def export_to_gtlf(name):
    """
    Экспортирует документ в формат GLTF.

    Args:
        name (str): имя файла для экспорта

    Errors:
        RuntimeError: если не удалось сохранить документ
    """

    c4d.StatusSetText("Exporting " + name)
    if not c4d.documents.SaveDocument(
        doc,
        pwd_gtlf + str(current_using_vals[-count_copy]),
        c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST,
        1041129,
    ):
        raise RuntimeError("Failed to save the document.")


def is_forbidden(names):
    """
    Проверяет, является ли какое-либо из заданных имен запрещенным.

    Args:
        names (list): Список строк, представляющих имена объектов.

    Returns:
        bool: True, если какое-либо из заданных имен запрещенное, False в противном случае.
    """
    for i in forb_list:
        if len(i) == 0:
            continue
        if all(b in names for b in i):
            return True
    return False


def main():
    """
    Генерирует 3D-модели, случайным образом выбирая и комбинируя различные объекты
    из разных категорий, таких как очки, маски, ювелирные изделия, головные уборы,
    одежда, волосы, глаза и специальные аксессуары. Функция также проверяет наличие
    ограничений на комбинации и, при необходимости, перегенерирует их.
    Сгенерированные модели затем устанавливаются для отображения в редакторе и рендеринга.
    """

    global count_copy
    done = set()
    o = doc.GetObjects()
    glasses = o[0].GetChildren()
    masks = o[1].GetChildren()
    jewelery = o[2].GetChildren()
    headgear = o[3].GetChildren()
    clothes = o[4].GetChildren()
    hairs = o[5].GetChildren()
    eyes = o[6].GetChildren()
    special_accessories = o[7].GetChildren()
    glasses_name = [i.GetName() for i in glasses]
    masks_name = [i.GetName() for i in masks]
    jews_name = [i.GetName() for i in jewelery]
    headgear_name = [i.GetName() for i in headgear]
    clothes_name = [i.GetName() for i in clothes]
    hairs_name = [i.GetName() for i in hairs]
    eyes_name = [i.GetName() for i in eyes]
    special_accessories_name = [i.GetName() for i in special_accessories]

    for i in glasses:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in masks:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in jewelery:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in headgear:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in clothes:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in hairs:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in eyes:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    for i in special_accessories:
        i[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        i[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
    c = 0
    for i in restricts:
        # для каждого i-ого генерить кол-во указанное в нем айди, затем
        # проверять попадает ли под рестрикт любое из других значений с помощью поиска по именам
        # если рестрикт превышен - перегенреировать
        while i[2] > 0:
            if count_copy <= 0:
                return
            c4d.StatusSetBar(((float(c) + 1.0) / float(COUNT + pre_count)) * 100.0)
            while True:
                glasses_id = random.randint(0, len(glasses) - 1)
                masks_id = random.randint(0, len(masks) - 1)
                jewelery_id = random.randint(0, len(jewelery) - 1)
                headgear_id = random.randint(0, len(headgear) - 1)
                clothes_id = random.randint(0, len(clothes) - 1)
                hairs_id = random.randint(0, len(hairs) - 1)
                eyes_id = random.randint(0, len(eyes) - 1)
                special_accessories_id = random.randint(0, len(special_accessories) - 1)

                if i[0] == "glasses":
                    glasses_id = glasses_name.index(i[1])
                elif i[0] == "masks":
                    masks_id = masks_name.index(i[1])
                elif i[0] == "jewelry":
                    jewelery_id = jews_name.index(i[1])
                elif i[0] == "headgear":
                    headgear_id = headgear_name.index(i[1])
                elif i[0] == "clothes":
                    clothes_id = clothes_name.index(i[1])
                elif i[0] == "hairs":
                    hairs_id = hairs_name.index(i[1])
                elif i[0] == "eyes":
                    eyes_id = eyes_name.index(i[1])
                elif i[0] == "special_accessories":
                    special_accessories_id = special_accessories_name.index(i[1])

                if HEADGEAR_CONFLICT and i[0] == "headgear":
                    hairs_id = -1
                elif HEADGEAR_CONFLICT and i[0] == "hairs":
                    headgear_id = -1
                elif HEADGEAR_CONFLICT:
                    r = random.randint(0, 1)
                    if r:
                        hairs_id = -1
                    else:
                        headgear_id = -1

                if (
                    glasses_id,
                    masks_id,
                    jewelery_id,
                    headgear_id,
                    clothes_id,
                    hairs_id,
                    eyes_id,
                    special_accessories_id,
                ) not in done:
                    model_names = (
                        glasses[glasses_id].GetName(),
                        masks[masks_id].GetName(),
                        jewelery[jewelery_id].GetName(),
                        headgear[headgear_id].GetName(),
                        clothes[clothes_id].GetName(),
                        hairs[hairs_id].GetName(),
                        eyes[eyes_id].GetName(),
                        special_accessories[special_accessories_id].GetName(),
                    )
                    if hairs_id == -1:
                        model_names = (
                            glasses[glasses_id].GetName(),
                            masks[masks_id].GetName(),
                            jewelery[jewelery_id].GetName(),
                            headgear[headgear_id].GetName(),
                            clothes[clothes_id].GetName(),
                            "NULL",
                            eyes[eyes_id].GetName(),
                            special_accessories[special_accessories_id].GetName(),
                        )
                    if headgear_id == -1:
                        model_names = (
                            glasses[glasses_id].GetName(),
                            masks[masks_id].GetName(),
                            jewelery[jewelery_id].GetName(),
                            "NULL",
                            clothes[clothes_id].GetName(),
                            hairs[hairs_id].GetName(),
                            eyes[eyes_id].GetName(),
                            special_accessories[special_accessories_id].GetName(),
                        )
                    print(model_names)
                    if is_forbidden(model_names):
                        done.add(
                            (
                                glasses_id,
                                masks_id,
                                jewelery_id,
                                headgear_id,
                                clothes_id,
                                hairs_id,
                                eyes_id,
                                special_accessories_id,
                            )
                        )
                        continue
                    bad = False
                    for z in model_names:
                        if bad:
                            break
                        for xa in restricts:
                            if xa[1] == z:
                                if xa[2] <= 0:
                                    done.add(
                                        (
                                            glasses_id,
                                            masks_id,
                                            jewelery_id,
                                            headgear_id,
                                            clothes_id,
                                            hairs_id,
                                            eyes_id,
                                            special_accessories_id,
                                        )
                                    )
                                    bad = True
                                    break
                    if bad:
                        continue
                    for z in model_names:
                        for xa in restricts:
                            if xa[1] == z:
                                xa[2] -= 1
                    break

            glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
            special_accessories[special_accessories_id][
                c4d.ID_BASEOBJECT_VISIBILITY_RENDER
            ] = 0

            glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
            special_accessories[special_accessories_id][
                c4d.ID_BASEOBJECT_VISIBILITY_EDITOR
            ] = 0

            if hairs_id == -1:
                hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
                hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1

            if headgear_id == -1:
                headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
                headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1

            name = (
                str(glasses_id)
                + "_"
                + str(masks_id)
                + "_"
                + str(jewelery_id)
                + "_"
                + str(headgear_id)
                + "_"
                + str(eyes_id)
                + "_"
                + str(special_accessories_id)
                + "_"
                + str(current_using_vals[-count_copy])
            )
            model_names = (
                glasses[glasses_id].GetName(),
                masks[masks_id].GetName(),
                jewelery[jewelery_id].GetName(),
                headgear[headgear_id].GetName(),
                clothes[clothes_id].GetName(),
                hairs[hairs_id].GetName(),
                eyes[eyes_id].GetName(),
                special_accessories[special_accessories_id].GetName(),
            )

            render(name)

            current_number: int = current_using_vals[-count_copy]
            nft = dict()

            # nft["NUMBER"] = current_number
            nft["description"] = ""  # тут должно быть ваше описание
            nft["external_url"] = ""
            nft["image"] = ""  # тут должна быть ссылка на эту картинку в хранилище
            nft["name"] = f"Noxa Identity #{current_number}"
            nft["attributes"] = []
            nft["attributes"].append(
                {"display_type": "string", "trait_type": "Class", "value": CLASS_NAME}
            )
            if model_names[0] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Eyewear",
                        "value": model_names[0],
                    }
                )
            if model_names[1] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Masks",
                        "value": model_names[1],
                    }
                )
            if model_names[2] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Jewelry",
                        "value": model_names[2],
                    }
                )
            if headgear_id != -1 and model_names[3] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Headgear",
                        "value": model_names[3],
                    }
                )
            if model_names[4] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Clothes",
                        "value": model_names[4],
                    }
                )
            if hairs_id != -1 and model_names[5] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Hairs",
                        "value": model_names[5],
                    }
                )
            if model_names[6] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Eyes",
                        "value": model_names[6],
                    }
                )
            if model_names[7] != "NULL":
                nft["attributes"].append(
                    {
                        "display_type": "string",
                        "trait_type": "Special Accessories",
                        "value": model_names[7],
                    }
                )
            nfts.append({current_number: nft})
            nft_names_saving()

            print(model_names)

            glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            special_accessories[special_accessories_id][
                c4d.ID_BASEOBJECT_VISIBILITY_RENDER
            ] = 1

            glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            special_accessories[special_accessories_id][
                c4d.ID_BASEOBJECT_VISIBILITY_EDITOR
            ] = 1
            c += 1
            done.add(
                (
                    glasses_id,
                    masks_id,
                    jewelery_id,
                    headgear_id,
                    clothes_id,
                    hairs_id,
                    eyes_id,
                    special_accessories_id,
                )
            )

    for c in range(COUNT):
        if count_copy <= 0:
            return
        c4d.StatusSetBar(
            ((float(c + pre_count) + 1.0) / float(COUNT + pre_count)) * 100.0
        )
        while True:
            glasses_id = random.randint(0, len(glasses) - 1)
            masks_id = random.randint(0, len(masks) - 1)
            jewelery_id = random.randint(0, len(jewelery) - 1)
            headgear_id = random.randint(0, len(headgear) - 1)
            clothes_id = random.randint(0, len(clothes) - 1)
            hairs_id = random.randint(0, len(hairs) - 1)
            eyes_id = random.randint(0, len(eyes) - 1)
            special_accessories_id = random.randint(0, len(special_accessories) - 1)

            if HEADGEAR_CONFLICT:
                r = random.randint(0, 1)
                if r:
                    hairs_id = -1
                else:
                    headgear_id = -1

            if (
                glasses_id,
                masks_id,
                jewelery_id,
                headgear_id,
                clothes_id,
                hairs_id,
                eyes_id,
                special_accessories_id,
            ) not in done:
                model_names = (
                    glasses[glasses_id].GetName(),
                    masks[masks_id].GetName(),
                    jewelery[jewelery_id].GetName(),
                    headgear[headgear_id].GetName(),
                    clothes[clothes_id].GetName(),
                    hairs[hairs_id].GetName(),
                    eyes[eyes_id].GetName(),
                    special_accessories[special_accessories_id].GetName(),
                )
                if hairs_id == -1:
                    model_names = (
                        glasses[glasses_id].GetName(),
                        masks[masks_id].GetName(),
                        jewelery[jewelery_id].GetName(),
                        headgear[headgear_id].GetName(),
                        clothes[clothes_id].GetName(),
                        "NULL",
                        eyes[eyes_id].GetName(),
                        special_accessories[special_accessories_id].GetName(),
                    )
                if headgear_id == -1:
                    model_names = (
                        glasses[glasses_id].GetName(),
                        masks[masks_id].GetName(),
                        jewelery[jewelery_id].GetName(),
                        "NULL",
                        clothes[clothes_id].GetName(),
                        hairs[hairs_id].GetName(),
                        eyes[eyes_id].GetName(),
                        special_accessories[special_accessories_id].GetName(),
                    )

                if any(i in (j[1] for j in restricts) for i in model_names):
                    done.add(
                        (
                            glasses_id,
                            masks_id,
                            jewelery_id,
                            headgear_id,
                            clothes_id,
                            hairs_id,
                            eyes_id,
                            special_accessories_id,
                        )
                    )
                    continue

                if is_forbidden(model_names):
                    done.add(
                        (
                            glasses_id,
                            masks_id,
                            jewelery_id,
                            headgear_id,
                            clothes_id,
                            hairs_id,
                            eyes_id,
                            special_accessories_id,
                        )
                    )
                    continue
                break

        glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 0
        special_accessories[special_accessories_id][
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER
        ] = 0

        glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 0
        special_accessories[special_accessories_id][
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR
        ] = 0

        if hairs_id == -1:
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
            hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1

        if headgear_id == -1:
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
            headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1

        name = (
            str(glasses_id)
            + "_"
            + str(masks_id)
            + "_"
            + str(jewelery_id)
            + "_"
            + str(headgear_id)
            + "_"
            + str(eyes_id)
            + "_"
            + str(special_accessories_id)
            + "_"
            + str(current_using_vals[-count_copy])
        )
        model_names = (
            glasses[glasses_id].GetName(),
            masks[masks_id].GetName(),
            jewelery[jewelery_id].GetName(),
            headgear[headgear_id].GetName(),
            clothes[clothes_id].GetName(),
            hairs[hairs_id].GetName(),
            eyes[eyes_id].GetName(),
            special_accessories[special_accessories_id].GetName(),
        )

        render(name)
        current_number: int = current_using_vals[-count_copy]
        nft = dict()
        # nft["NUMBER"] = current_number
        nft["description"] = ""  # тут должно быть ваше описание
        nft["external_url"] = ""
        nft["image"] = ""  # тут должна быть ссылка на эту картинку в хранилище
        nft["name"] = f"Noxa Identity #{current_number}"
        nft["attributes"] = []
        nft["attributes"].append(
            {"display_type": "string", "trait_type": "Class", "value": CLASS_NAME}
        )
        if model_names[0] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Eyewear",
                    "value": model_names[0],
                }
            )
        if model_names[1] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Masks",
                    "value": model_names[1],
                }
            )
        if model_names[2] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Jewelry",
                    "value": model_names[2],
                }
            )

        if headgear_id != -1 and model_names[3] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Headgear",
                    "value": model_names[3],
                }
            )
        if model_names[4] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Clothes",
                    "value": model_names[4],
                }
            )
        if hairs_id != -1 and model_names[5] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Hairs",
                    "value": model_names[5],
                }
            )
        if model_names[6] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Eyes",
                    "value": model_names[6],
                }
            )
        if model_names[7] != "NULL":
            nft["attributes"].append(
                {
                    "display_type": "string",
                    "trait_type": "Special Accessories",
                    "value": model_names[7],
                }
            )

        nfts.append({str(current_number): nft})
        nft_names_saving()

        print(model_names)

        glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = 1
        special_accessories[special_accessories_id][
            c4d.ID_BASEOBJECT_VISIBILITY_RENDER
        ] = 1

        glasses[glasses_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        masks[masks_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        jewelery[jewelery_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        headgear[headgear_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        clothes[clothes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        hairs[hairs_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        eyes[eyes_id][c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        special_accessories[special_accessories_id][
            c4d.ID_BASEOBJECT_VISIBILITY_EDITOR
        ] = 1
        done.add(
            (
                glasses_id,
                masks_id,
                jewelery_id,
                headgear_id,
                clothes_id,
                hairs_id,
                eyes_id,
                special_accessories_id,
            )
        )
        print("Completed " + str(c + 1) + " of " + str(COUNT))


def test():
    """
    Тестовая функция для проверки работы скрипта.
    """
    o = doc.GetObjects()
    glasses = o[0].GetChildren()
    g = glasses[0]
    print(g.GetName())
    g_child = g.GetChildren()

    sym_child = g_child[0].GetChildren()
    textures = sym_child[0].GetTags()
    print(textures[0].GetMaterial())


if __name__ == "__main__":
    start_time = time.time()
    main()

    nft_names_saving()
    used_numbers_dumping()
    gui.MessageDialog((time.time() - start_time))
