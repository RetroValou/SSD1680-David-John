#decoupage = (110, 200)
#file = "C:/Users/linkd/Desktop/img_convert/Menu_img_multi.bmp"

decoupage = (110, 200)
file = "C:/Users/linkd/Desktop/img_convert/Menu_img_fond.bmp"

#decoupage = (32, 32)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/projectile_before_nothing.bmp"

#decoupage = (32, 32)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/projectile_before_multi.bmp"

#decoupage = (60, 60)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/guy_multi.bmp"

#decoupage = (60, 60)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/guy_multi.bmp"

#decoupage = (60, 60)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/protect_multi.bmp"

#decoupage = (1, 100)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/line.bmp"

#decoupage = (60, 30)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/tuyau_up.bmp"

#decoupage = (60, 60)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/button_multi.bmp"

#decoupage = (32, 20)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/dodo_david_fix.bmp"

#decoupage = (32, 20)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/dodo_david.bmp"

#decoupage = (22, 36)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/david_angry.bmp"

#decoupage = (60, 16)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/projectile_multi.bmp"

#decoupage = (40, 1)
#file = "C:/Users/linkd/Desktop/img_convert/rythme/line_horizontal.bmp"

decoupage = (60, 32)
file = "C:/Users/linkd/Desktop/img_convert/fabric/projectile_multi.bmp"

#decoupage = (49, 80)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/canon.bmp"

#decoupage = (60, 60)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/pond_multi.bmp"

#decoupage = (8, 8)
#file = "C:/Users/linkd/Desktop/img_convert/number_inv.bmp"

#decoupage = (8, 8)
#file = "C:/Users/linkd/Desktop/img_convert/number.bmp"

#decoupage = (40, 16)
#file = "C:/Users/linkd/Desktop/img_convert/highscore.bmp"

#decoupage = (72, 8)
#file = "C:/Users/linkd/Desktop/img_convert/temp_mode.bmp"

#decoupage = (64, 64)
#file = "C:/Users/linkd/Desktop/img_convert/fabric/escalator.bmp"

#decoupage = (32, 32)
#file = "C:/Users/linkd/Desktop/img_convert/fabric/before_destroy.bmp"

#decoupage = (20, 20)
#file = "C:/Users/linkd/Desktop/img_convert/Climber/life.bmp"

#decoupage = (20, 20)
#file = "C:/Users/linkd/Desktop/img_convert/Avignon/life.bmp"

from PIL import Image
import numpy as np


image = Image.open(file)

image = np.clip(np.array(image, dtype = np.uint8), 0, 1)

nb_x_d = int(image.shape[1]/decoupage[0])
nb_y_d = int(image.shape[0]/decoupage[1])
print(nb_x_d, nb_y_d)
result = []
for y_d in range(nb_y_d):
    for x_d in range(nb_x_d):
        print(str(x_d) + " " + str(x_d+decoupage[0]))
        print(str(y_d) + " " + str(y_d+decoupage[1]))
        tmp_result = [decoupage[0]]
        img_d = image[y_d*decoupage[1]:(y_d+1)*decoupage[1],x_d*decoupage[0]:(x_d+1)*decoupage[0]]
        for line in range(img_d.shape[0]):
            text = np.array(img_d, dtype = str)[line]
            text = int("".join(text), 2)
            tmp_result.append(text)
        result.append(tmp_result)
import json
   
   
with open(file[:-3]+"json", 'w') as f:
    # indent=2 is not needed but makes the file human-readable 
    # if the data is nested
    json.dump(result, f, indent=2) 



def DEBUG_show_img_test(img):
    for line in range(1,len(img)):
        txt = bin(img[line])[2:]
        for i in range(len(txt), img[0]):
            txt = "0"+txt
        print(txt)
        
        
for img in result:
    print(" ")
    DEBUG_show_img_test(img) 