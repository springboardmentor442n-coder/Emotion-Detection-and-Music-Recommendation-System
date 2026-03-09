import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint

# =========================
# DATA PATHS
# =========================

train_dir = "ml/data/raw/fer2013/train"
test_dir = "ml/data/raw/fer2013/test"

# =========================
# DATA GENERATORS
# =========================

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(48,48),
    batch_size=64,
    color_mode="grayscale",
    class_mode="categorical"
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(48,48),
    batch_size=64,
    color_mode="grayscale",
    class_mode="categorical"
)

# =========================
# MODEL 
# =========================

model = Sequential()

# BLOCK 1
model.add(Conv2D(64, (5,5), padding='same', activation='relu', input_shape=(48,48,1)))
model.add(Conv2D(64, (5,5), padding='same', activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))

# BLOCK 2
model.add(Conv2D(128, (5,5), padding='same', activation='relu'))
model.add(Conv2D(128, (5,5), padding='same', activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))

# BLOCK 3
model.add(Conv2D(256, (3,3), padding='same', activation='relu'))
model.add(Conv2D(256, (3,3), padding='same', activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))

# FULLY CONNECTED
model.add(Flatten())

model.add(Dense(128))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Dropout(0.2))

model.add(Dense(train_data.num_classes))
model.add(Activation('softmax'))

# =========================
# COMPILE
# =========================

optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(
    loss='categorical_crossentropy',
    optimizer=optimizer,
    metrics=['accuracy']
)

model.summary()

# =========================
# SAVE BEST MODEL
# =========================

checkpoint = ModelCheckpoint(
    "best_emotion_model.keras",
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

# =========================
# TRAIN
# =========================

history = model.fit(
    train_data,
    validation_data=test_data,
    epochs=20,
    callbacks=[checkpoint],
    shuffle=True
)

# =========================
# SAVE FINAL MODEL
# =========================

model.save("ml/models/emotion_model.keras")

print("Training completed successfully")