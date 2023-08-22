from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.http import JsonResponse,StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import PlRiver3857, PlPlot3857,Inlandwater,PlPlot3857
# from .serializers import *
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from django.contrib.gis.measure import D
import json

from django.contrib.gis.db.models.functions import Transform, Area, Distance
import json
import random

# Create your views here.

# def front(request):
#     context = { }
#     return render(request, "index.html", context)

@api_view(['GET', 'POST'])
def complex_Search(request):
    if request.method == 'GET':
        print(request.data)
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        print('complex search',request.data)
        data = request.data.get('data')

        land_option = data['landOption']
        l_min_area = land_option['l_min_area']
        l_max_area = land_option['l_max_area']
        l_min_aed = land_option['l_min_aed']
        l_max_aed = land_option['l_max_aed']

        if l_min_area != '' or l_max_area != '':
            if l_min_area == '':
                sqlForRegions = '''
                    SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_plot3857 WHERE area <= %(l_max_area)s;
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForRegions,{'l_max_area': l_max_area})
                    overlapping_regions = cursor.fetchall()
            if l_max_area == '':
                sqlForRegions = '''
                    SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_plot3857 WHERE area >= %(l_min_area)s;
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForRegions,{'l_min_area': l_min_area})
                    overlapping_regions = cursor.fetchall()
            else:
                if l_min_area <= l_max_area:
                    sqlForRegions = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_plot3857 WHERE area >= %(l_min_area)s AND area <= %(l_max_area)s;
                    '''
                    with connection.cursor() as cursor:
                        cursor.execute(sqlForRegions,{'l_max_area': l_max_area, 'l_min_area': l_min_area})
                        overlapping_regions = cursor.fetchall()
        
        # item_to_search = []
        # for item in data['toSearch']:
        #     if data['toSearch'][item]:
        #         item_to_search.append(item)

        # Get variables each

        r_option = data['options']['river']

        r_distance_isset = r_option['distance']['isSet']
        r_distance_mindistance_isset = r_option['distance']['minDistance']['isSet']
        r_distance_mindistance = r_option['distance']['minDistance']['value']
        r_distance_maxdistance = r_option['distance']['maxDistance']['value']

        r_length_isset = r_option['length']['isSet']
        r_length_minlength = r_option['length']['minLength']['value']
        r_length_maxlength_isset = r_option['length']['maxLength']['isSet']
        r_length_maxlength = r_option['length']['maxLength']['value']

        r_width_isset = r_option['width']['isSet']
        r_width_minwidth = r_option['width']['minWidth']['value']
        r_width_maxwidth_isset = r_option['width']['maxWidth']['isSet']
        r_width_maxwidth = r_option['width']['maxWidth']['value']

        r_name_isset = r_option['name']['isSet']
        r_name_method = r_option['name']['method']['value']
        r_name_reference = r_option['name']['reference']['value']

        # r_length = data.get('R_Length')
        # r_width = data.get('R_Width')
        # l_area = data.get('L_Area')
        # distance = data.get('R_Distance')
# only river relation
        # sqlForRegions = '''
        # SELECT
        #     ST_AsGeoJSON(ST_Union(ST_Transform(pl_plot3857.geom, 3857)))
        # FROM pl_plot3857
        # INNER JOIN (
        #     SELECT ST_Buffer(ST_Union(ST_Transform(geom, 3857)), 50) AS buffer_geom
        #     FROM pl_river3857
        #     WHERE dlug >= 100 AND r_width >= 20
        # ) AS pl_river3857_buffer
        # ON ST_Intersects(pl_plot3857.geom, pl_river3857_buffer.buffer_geom);
        # '''
# river and lake
        # sqlForRegions = '''
        #         SELECT
        #             ST_AsGeoJSON(ST_Union(ST_Transform(pl_plot3857.geom, 3857)))
        #         FROM
        #             pl_plot3857
        #         INNER JOIN (
        #             SELECT ST_Buffer(
        #                 ST_Union(
        #                     ST_Transform(ST_Force2D(geom), 3857)
        #                 ),
        #                %(distance)s
        #             ) AS buffer_geom
        #             FROM (
        #                 SELECT geom
        #                 FROM pl_river3857
        #                 WHERE dlug >=  %(r_length)s AND r_width >= %(r_width)s
        #                 UNION ALL
        #                 SELECT shape
        #                 FROM inlandwater
        #                 WHERE area >=  %(l_area)s
        #             ) AS water_geom
        #         ) AS water_buffer
        #         ON ST_Intersects(pl_plot3857.geom, water_buffer.buffer_geom);
        #     '''
        # l_area = 10
        sqlForRegions = '''
            SELECT
                ST_AsGeoJSON(ST_Union(ST_Transform(pl_plot3857.geom, 3857)))
            FROM
                pl_plot3857
            INNER JOIN (
                SELECT ST_Buffer(
                    ST_Union(
                        ST_Transform(ST_Force2D(geom), 3857)
                    ),
                    %(r_distance_maxdistance)s
                ) AS buffer_geom
                FROM (
                    SELECT geom
                    FROM pl_river3857
                    WHERE dlug >=  %(r_length_minlength)s AND r_width >= %(r_width_minwidth)s
                ) AS water_geom
            ) AS water_buffer
            ON ST_Intersects(pl_plot3857.geom, water_buffer.buffer_geom);
        '''


        with connection.cursor() as cursor:
            cursor.execute(sqlForRegions,{'r_distance_maxdistance': r_distance_maxdistance, 'r_length_minlength': r_length_minlength, 'r_width_minwidth': r_width_minwidth})
            overlapping_regions = cursor.fetchall()

        print('overlapping_regions')
        return Response(overlapping_regions)
    
# def complex_Search(request):
#     if request.method == 'GET':
#         print(request.data)
#         return Response(status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         print(request.data)
#         data = request.data.get('data')
#         l_area =data.get('L_Area')
#         l_distance =data.get('L_Distance')
#         # filter_lake_condition = {'area': float(l_area)}
#         r_length = data.get('R_Length')
#         r_width = data.get('R_Width')
#         r_distance = data.get('R_Distance')
#         filter_river_condition = {'dlug__gte': float(r_length),
#                             'r_width__gte': float(r_width)
#                             }
#         # riverfilter = PlRiver3857.objects.filter(**filter_river_condition)
#         # print(f"river_count: {riverfilter.count()}")
#         # print(f"riverfilter: {riverfilter[0]}")

#         # Define the buffer distance around the river range (2000m in this case)
#         # Construct the SQL statement
#         sqlForRiver = '''
#             SELECT ST_AsGeoJSON(ST_Union(ST_Buffer(geom, %(buffer_distance)s))) AS merged_geojson
#             FROM pl_river3857
#             WHERE dlug >= %(r_length)s AND r_width >= %(r_width)s
#         '''
#         # sqlForLake = '''
#         #     SELECT ST_AsGeoJSON(ST_Union(ST_Buffer(ST_Transform(shape, 3857), %(buffer_distance)s))) AS merged_geojson FROM inlandwater WHERE area >= %(l_Area)s;
#         # '''
#         # Execute the raw SQL query
#         with connection.cursor() as cursor:
#             cursor.execute(sqlForRiver, {'buffer_distance': r_distance, 'r_length': r_length, 'r_width': r_width})
#             river_merged_geojson = cursor.fetchone()[0]
#         # with connection.cursor() as cursor:
#         #     cursor.execute(sqlForLake, {'buffer_distance': l_distance, 'l_Area': l_area})
#         #     lake_merged_geojson = cursor.fetchone()[0]
#         RiverGeoData = river_merged_geojson
#         # LakeGeoData = lake_merged_geojson

#         # geoata = serialize("geojson", riverfilter, geometry_field="geom", fields=["naz_rzeki"])
        
        
#         # river_queryset = PlRiver3857.objects.select_related('') #annotate(distance=Distance('geom', models.F('plot__geom'))).filter(distance__lte=1000)
#         # condition = {'area__lte': float(5000)}
#         # plotfilter = PlPlot3857.objects.filter(**condition)
#         # print(f"plot_count: {plotfilter.count()}")
        
#         # plot_temp = PlPlot3857.objects.filter(geom__area_lte=500)
        
#         #create a buffer around the polyline object
#         # buffer_polyline =
#         # for riverline in riverfilter:
#         #     #create a buffer around the riverline object
#         #     buffer_polyline = riverline.geom.buffer(1000)
#         #     print(buffer_polyline)
#             # contain_plot = plotfilter.filter(geom__intersects=buffer_polyline )
#             # if contain_plot.count() > 0:
#             #     print('--------------------------')
#             #     print(contain_plot)
#             #     print('**************************************')
        
#         # # print(f"plot_temp {plot_temp.count()}")
#         # for plot in plotfilter:
#         #     # print(plot.geom.centroid)
#         #     point = plot.geom.centroid
#         #     data = riverfilter.filter(geom__distance_lte=(point, D(km=0.001)))
#         #     if data.count() > 0:
#         #         print("--------------------")
#         #         print(data)
#         #         print("-------------------")
        
#         # plotfilter.prefetch_related(riverfilter)
        
#         # geojson = serializers('geojson', queryset, geometry_field='geom')
        
#         # print(geojson)
#         json_data = json.dumps({'river':RiverGeoData})
#         # json_data = json.dumps({'river':RiverGeoData,'lake':LakeGeoData})
#         return JsonResponse(json_data, safe=False)
@api_view(['GET', 'POST'])
def all_Search(request):
    if request.method == 'GET':
        print(request.data)
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        print('river req')
        print(request.data)
        data = request.data.get('data')
        r_length = data.get('R_length')
        r_width = data.get('R_width')
        l_area_min = data.get('L_Area_min')
        l_area_max = data.get('L_Area_max')
        f_area_min = data.get('F_Area_min')
        f_area_max = data.get('F_Area_max')
        p_area_min = data.get('P_Area_min')
        p_area_max = data.get('P_Area_max')
        json_data=[]
        if r_length:
            if r_width:
                sqlForRiver = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_river3857 WHERE dlug >= %(r_length)s and r_width >= %(r_width)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForRiver, {'r_length': r_length,'r_width': r_width})
                    riverfilter = cursor.fetchone()[0]
                print("river_count1" )
            else:
                sqlForRiver = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_river3857 WHERE dlug >= %(r_length)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForRiver, {'r_length': r_length})
                    riverfilter = cursor.fetchone()[0]
                    print("river_count2" )
            json_data = json.dumps({'key':'R','val':riverfilter})
        elif l_area_min:
            if l_area_max:
                sqlForLake = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(shape, 3857))) AS merged_geojson FROM inlandwater WHERE area >= %(l_Area_min)s and area >= %(l_Area_max)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForLake, {'l_Area_min': l_area_min,'l_Area_max': l_area_max})
                    lakefilter = cursor.fetchone()[0]
                print("lake_count1" )
            else:
                sqlForLake = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(shape, 3857))) AS merged_geojson FROM inlandwater WHERE area >= %(l_Area_min)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForLake, {'l_Area_min': l_area_min})
                    lakefilter = cursor.fetchone()[0]
                    print("lake_count2" )
            json_data = json.dumps({'key':'L','val':lakefilter})
        elif f_area_min:
            if f_area_max:
                sqlForForest = '''
                    SELECT ST_AsGeoJSON(ST_Union(ST_Transform(way, 3857))) AS merged_geojson FROM planet_osm_polygon WHERE way_area >= %(f_Area_min)s AND way_area >= %(f_Area_max)s;
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForForest, {'f_Area_min': f_area_min,'f_Area_max': f_area_max})
                    forestfilter = cursor.fetchone()[0]
                print("forest_count1" ) 
            else:
                sqlForForest = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(way, 3857))) AS merged_geojson FROM planet_osm_polygon WHERE way_area >= %(f_Area_min)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForForest, {'f_Area_min': f_area_min})
                    forestfilter = cursor.fetchone()[0]
                    print("forest_count2" )
            json_data = json.dumps({'key':'F','val':forestfilter})
        elif p_area_min:
            if p_area_max:
                sqlForLand = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_plot3857 WHERE area >= %(p_Area_min)s AND way_area >= %(p_Area_max)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForLand, {'p_Area_min': p_area_min,'p_Area_max': p_area_max})
                    landfilter = cursor.fetchone()[0]
                print("land_count1" ) 
            else:
                sqlForLand = '''
                        SELECT ST_AsGeoJSON(ST_Union(ST_Transform(geom, 3857))) AS merged_geojson FROM pl_plot3857 WHERE area >= %(p_Area_min)s;
                    '''
                with connection.cursor() as cursor:
                    cursor.execute(sqlForLand, {'p_Area_min': p_area_min})
                    landfilter = cursor.fetchone()[0]
                print("land_count1" ) 
            json_data = json.dumps({'key':'P','val':landfilter})
        return JsonResponse(json_data, safe=False)

@api_view(['GET', 'POST'])
def point_Search(request):
    if request.method == 'GET':
        print(request.data)
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        print('river req')
        print(request.data)
        json_data=[]
        datas = request.data.get('data')
        data=datas['data']
        sqlForHospital = '''
                SELECT ST_AsGeoJSON(ST_Union(ST_Transform(way, 3857))) AS merged_geojson FROM planet_osm_point WHERE amenity=%(parameter)s;
            '''
        with connection.cursor() as cursor:
            cursor.execute(sqlForHospital,{'parameter':data})
            datafilter = cursor.fetchone()[0]
        print(data) 
        json_data = json.dumps({'key':data,'val':datafilter})
        return JsonResponse(json_data, safe=False)