import gpxpy.gpx

def get_gpx_metric(gpx_bytes):
    gpx_metric = []
    gpx = gpxpy.parse(gpx_bytes)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Handle gpx general information
                time = point.time
                lat = point.latitude
                long = point.longitude
                atemp = hr = cad = power = 0

                for extension in point.extensions:
                    isTpe = 'TrackPointExtension' in extension.tag

                    if isTpe:
                        # Handle track point extension values
                        for tpe in extension:
                            atemp = tpe.text if 'atemp' in tpe.tag else 0
                            hr = tpe.text if 'hr' in tpe.tag else 0
                            cad = tpe.text if 'cad' in tpe.tag else 0

                    else:
                        # Handle power data
                        power = extension.text if 'power' in extension.tag else 0

                gpx_metric.append({ 'time':time, 'lat':lat, 'long':long, 'atemp':atemp, 'hr':hr, 'cad':cad, 'power':power })

    return gpx_metric


