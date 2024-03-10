import datetime
import math
import random

import cv2
from geopy import distance
import gpxpy

class GPXUtils:
    @staticmethod
    def extract_gpx_info(file_path):
        # Read GPX file
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        # Extract basic information
        info = {
            'name': gpx.name,
            'description': gpx.description,
            'author': gpx.author_name,
            'email': gpx.author_email,
            'time': gpx.time,
            'duration': GPXUtils.calculate_duration(gpx),
            'distance': GPXUtils.calculate_distance(gpx),
            'elevation_gain': GPXUtils.calculate_elevation_gain(gpx),
            'elevation_loss': GPXUtils.calculate_elevation_loss(gpx),
            'max_elevation': GPXUtils.calculate_max_elevation(gpx),
            'min_elevation': GPXUtils.calculate_min_elevation(gpx),
            'start_point': GPXUtils.get_start_point(gpx),
            'end_point': GPXUtils.get_end_point(gpx),
            'data_interval': GPXUtils.extract_gpx_data_interval(file_path)
        }

        return info

    @staticmethod
    def extract_gpx_data_interval(file_path):
        # Read GPX file
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        #1. Check total time/total datapoint = totalInterval
        #2. Calculate 20 intervals between two adjacent point = list rndInterval
        #3. Check if the all the intervals in rndInterval are totalInterval or very close to totalInterval
        # Extract data interval
        data_interval = []
        rnd_interval = []
        #collapse all segment point into an array
        allPoints = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    allPoints.append(point)

        # random int of length of allPoints
        rnd_index = []
        for i in range(20):
            rnd_index.append(random.randint(0, len(allPoints) - 1))
        for i in range(len(rnd_index) - 1):
            rnd_interval.append((allPoints[rnd_index[i]+ 1].time - allPoints[rnd_index[i]].time).total_seconds())
        # check if the max - min of rnd_interval is less than 0.01
        for i in range(len(rnd_interval)):
            if max(rnd_interval) - min(rnd_interval) < 0.01:
                data_interval.append(rnd_interval[i])
        return sum(data_interval) / len(data_interval)

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
            Calculate the great circle distance between two points
            on the earth (specified in decimal degrees)
            """
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        r = 6371  # Radius of earth in kilometers. Use 3959 for miles
        return c * r

    @staticmethod
    def velocity(lat1, lon1, lat2, lon2, time1, time2):
        # dist = distance.distance((lat1, lon1), (lat2, lon2)).m
        dist = GPXUtils.haversine_distance(lat1, lon1, lat2, lon2)
        time = (time2 - time1).total_seconds()
        return dist / time

    @staticmethod
    def gpx_datapoint_to_list(file_path):
        isInit = True
        fCount = 0
        prevTime = []
        prevLat = []
        prevLon = []
        datapoints = []
        with open(file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            startTime = gpx.tracks[0].segments[0].points[0].time
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        if fCount < 1:
                            isInit = False
                            fCount += 1
                            prevTime.append(point.time)
                            prevLat.append(point.latitude)
                            prevLon.append(point.longitude)
                            if fCount == 1:
                                point.velocity = 0
                            else:
                                lastTime = prevTime[fCount - 2]
                                lastLat = prevLat[fCount - 2]
                                lastLon = prevLon[fCount - 2]
                                point.velocity = GPXUtils.velocity(point.latitude, point.longitude, lastLat, lastLon,
                                                                   lastTime, point.time) * 1000
                        else:
                            fCount += 1
                            prevTime.append(point.time)
                            prevLat.append(point.latitude)
                            prevLon.append(point.longitude)
                            lastTime = prevTime.pop(0)
                            lastLat = prevLat.pop(0)
                            lastLon = prevLon.pop(0)
                            point.velocity = GPXUtils.velocity(point.latitude, point.longitude, lastLat, lastLon, lastTime, point.time) * 1000
                        point.power = point.extensions[0].text
                        point.timeFromStart = (point.time - startTime).total_seconds()

                        datapoints.append(point)

        return datapoints


    @staticmethod
    def calculate_duration(gpx):
        track = gpx.tracks[0] if gpx.tracks else None
        if track:
            return track.get_duration()
        return 0

    @staticmethod
    def calculate_distance(gpx):
        track = gpx.tracks[0] if gpx.tracks else None
        if track:
            return track.length_3d()
        return 0

    @staticmethod
    def calculate_elevation_gain(gpx):
        elevation_gain = 0
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation is not None and point.elevation > 0:
                        elevation_gain += point.elevation
        return elevation_gain

    @staticmethod
    def calculate_elevation_loss(gpx):
        elevation_loss = 0
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation is not None and point.elevation < 0:
                        elevation_loss += abs(point.elevation)
        return elevation_loss

    @staticmethod
    def calculate_max_elevation(gpx):
        max_elevation = float('-inf')
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation is not None and point.elevation > max_elevation:
                        max_elevation = point.elevation
        return max_elevation

    @staticmethod
    def calculate_min_elevation(gpx):
        min_elevation = float('inf')
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation is not None and point.elevation < min_elevation:
                        min_elevation = point.elevation
        return min_elevation

    @staticmethod
    def get_start_point(gpx):
        track = gpx.tracks[0] if gpx.tracks else None
        if track and track.segments:
            return track.segments[0].points[0]
        return None

    @staticmethod
    def get_end_point(gpx):
        track = gpx.tracks[0] if gpx.tracks else None
        if track and track.segments:
            last_segment = track.segments[-1]
            return last_segment.points[-1]
        return None

    @staticmethod
    def calculate_time_difference(gpx):
        start_time = GPXUtils.get_start_point(gpx).time
        end_time = GPXUtils.get_end_point(gpx).time
        return end_time - start_time

    @staticmethod
    def convert_time_to_milliseconds(time_str):
        minutes, seconds = time_str.split(':')
        total_milliseconds = int(minutes) * 60 + int(seconds)
        return total_milliseconds
    @staticmethod
    def find_frame_for_time_in_video(video_path, target_time):
        cap = cv2.VideoCapture(video_path)

        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        total_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS)

        frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Calculate frame rate (frames per second)
        frame_duration = 1.0 / frame_rate
        return int(GPXUtils.convert_time_to_milliseconds(target_time) * frame_rate)

