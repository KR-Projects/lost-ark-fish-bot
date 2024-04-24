## Fish Bot

This project originated from an interest in computer vision. In the game Lost Ark, fishing is possible, where one must pay attention to a yellow exclamation mark above the fishing rod. 
When this appears, a fish is on the hook. The initial approach involved recording some samples and training a model on this data. Unfortunately, this did not work well. The second approach involved isolating the exclamation mark and then generating various samples with it. This approach worked much better. There are some exceptions where the detection does not work, but this case occurs very rarely.
The model achieves an accuracy of >99%.

|Detected|Not detected|
| :---          | :---          |
|![](./dataset/real_test_set/fish/true%20(90).jpg)|![](./dataset/real_test_set/fish/true%20(82).jpg)|


### Demo
[![Watch the video](https://img.youtube.com/vi/P_PKHP6sJxM/hqdefault.jpg)](https://youtu.be/P_PKHP6sJxM)

### Hotkeys
|   Key         |   Function    |
| :---          | :---          |
| Arrow Up      | Reposition    |
| Arrow Down    | Enable/Disable|
| Arrow Left    | create sample no fish    |
| Arrow Right   | create sample fish       |

### Model

```java
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 rescaling (Rescaling)       (None, 200, 100, 3)       0         
                                                                 
 conv1 (Conv2D)              (None, 198, 98, 16)       448       
                                                                 
 conv2 (Conv2D)              (None, 196, 96, 16)       2320      
                                                                 
 pool1 (MaxPooling2D)        (None, 98, 48, 16)        0         
                                                                 
 conv3 (Conv2D)              (None, 96, 46, 64)        9280      
                                                                 
 conv4 (Conv2D)              (None, 94, 44, 64)        36928     
                                                                 
 pool2 (MaxPooling2D)        (None, 47, 22, 64)        0         
                                                                 
 flatten (Flatten)           (None, 66176)             0         
                                                                 
 dense (Dense)               (None, 20)                1323540   
                                                                 
 dense_1 (Dense)             (None, 20)                420       
                                                                 
 dense_2 (Dense)             (None, 20)                420       
...
Total params: 1,373,377
Trainable params: 1,373,377
Non-trainable params: 0
```
