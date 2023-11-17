import json
import os
import random
import boto3


class ParkingLot:
    def __init__(self, square_footage, spot_length=8, spot_width=12):
        self.spot_length = spot_length
        self.spot_width = spot_width
        self.total_spots = square_footage // (spot_length * spot_width)
        self.parking_lot = [None] * self.total_spots
        self.parking_map = {}

    def park_car(self, car, spot):
        if self.parking_lot[spot] is None:
            self.parking_lot[spot] = car
            self.parking_map[car.license_plate] = spot
            return True
        else:
            return False

    def map_vehicles_to_spots(self):
        return json.dumps(self.parking_map, indent=2)


class Car:
    def __init__(self, license_plate):
        self.license_plate = license_plate

    def __str__(self):
        return f"Car with license plate {self.license_plate}"

    def park(self, parking_lot, spot):
        if parking_lot.park_car(self, spot):
            print(f"{self} parked successfully in spot {spot}")
            return True
        else:
            print(
                f"Car with license plate {self.license_plate} could not be parked in spot {spot}. Spot is already occupied."
            )
            return False


class S3:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def upload(self, file_path, bucket_name, object_name):
        try:
            self.s3.upload_file(file_path, bucket_name, object_name)
            print(f"File uploaded successfully to {bucket_name}/{object_name}")
        except Exception as e:
            print(f"Error uploading file to S3: {e}")


def main():
    car_license_plates = [
        "ABC1234",
        "XYZ5678",
        "DEF9876",
        "GHI6543",
        "BCM3628",
    ]  # array of cars with random license plates
    cars = [Car(license_plate) for license_plate in car_license_plates]

    parking_lot_size = 2000  # Change this to the desired parking lot size
    parking_lot = ParkingLot(parking_lot_size)

    available_spots = list(range(len(parking_lot.parking_lot)))

    # Try to park each car in a random available spot until the parking lot is full or no cars are left.
    while cars and available_spots:
        car = cars.pop(0)  # Get the next car from the list
        spot = random.choice(available_spots)

        while not car.park(parking_lot, spot):
            # If the spot is occupied, remove it from available spots and try another one
            available_spots.remove(spot)
            if not available_spots:
                break
            spot = random.choice(available_spots)

    # Once the parking lot is full or no cars are left, exit the program
    print("Parking lot is full.")

    # Creating a JSON object mapping vehicles to parked spots
    parking_map_json = parking_lot.map_vehicles_to_spots()

    # Save the JSON object to a file on local.
    with open(f"{os.getcwd()}/parking_map.json", "w") as json_file:
        json_file.write(parking_map_json)

    # Code to upload the file to the S3 bucket can be added here
    # s3 = S3("aws_access_key_id", "aws_secret_access_key", "region_name")
    # s3.upload(f"{os.getcwd()}/parking_map.json", "bucket_name", "object_name")


if __name__ == "__main__":
    main()
