import board
import adafruit_mlx90614
import busio as io

i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

obj_temp = mlx.object_temperature
print("Object Temperature = ", obj_temp)
