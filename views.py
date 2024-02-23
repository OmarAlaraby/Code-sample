from project.settings import BASE_DIR
from .models import Housing, Transportation, Team, ECPCQ
from accounts.models import User, userManager

from .serializers import housingSerializers, teamSerializers, transportationSerializers, ecpcqSerializers
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from project.permissions import IsAdminOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# for cashing 
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


def is_registered(user , obj) :
    return user.is_authenticated and user in obj.users.all()


class housing_view(viewsets.ModelViewSet):
    queryset = Housing.objects.all()
    serializer_class = housingSerializers
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        
        if Housing.objects.exists() :
            return Response({"Error" : "you can't create two Housing registration in the same time"}, status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    # @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.get_serializer(queryset, many=True).data
        if queryset.exists() :
            data[0]['is_registered'] = is_registered(request.user, queryset.first())
        return Response(data)
    
    # @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    


class transportation_view(viewsets.ModelViewSet):
    queryset = Transportation.objects.all()
    serializer_class = transportationSerializers
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        
        if Transportation.objects.exists() :
            return Response({"Error" : "you can't create two Transportaion registraion in the same time"}, status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.get_serializer(queryset, many=True).data
        if queryset.exists() :
            data[0]['is_registered'] = is_registered(request.user, queryset.first())
        return Response(data)
    
    # @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    


class team_view(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = teamSerializers
    permission_classes = [IsAdminOrReadOnly]
    
    # @method_decorator(cache_page(60 * 15))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)
    
    # @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
class ecpcq_view(viewsets.ModelViewSet):
    queryset = ECPCQ.objects.all()
    serializer_class = ecpcqSerializers
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        
        if ECPCQ.objects.exists() :
            return Response({"Error" : "you can't create two ECPCQ registraion in the same time"}, status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.get_serializer(queryset, many=True).data
        if queryset.exists() :
            data[0]['is_registered'] = request.user.is_authenticated and request.user.ecpcq_team.exists()
        return Response(data)
    
    # @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
############## helpers ################

def coach_included(first_contestant, second_contestant, third_contestant) :
    checker_results = [False, []]
    if first_contestant.groups.filter(name='Coaches').exists() :
        checker_results[0] = True
        checker_results[1].append("You are a coach")
    
    if second_contestant.groups.filter(name='Coaches').exists() :
        checker_results[0] = True
        checker_results[1].append(f"{second_contestant.username} is a coach")
    
    if third_contestant.groups.filter(name='Coaches').exists() :
        checker_results[0] = True
        checker_results[1].append(f"{third_contestant.username} is a coach")

    return checker_results

def unregisters_users(first_contestant, second_contestant, third_contestant):
    if first_contestant.ecpcq_team.exists() :
        return False
    if second_contestant.ecpcq_team.exists() :
        return False
    if third_contestant.ecpcq_team.exists() :
        return False
    return True

def all_users_virified(first_contestant, second_contestant, third_contestant) :
    checker_results = [True, []]
    if not first_contestant.is_verified :
        checker_results[0] = False
        checker_results[1].append("You are not verified")
    
    if not second_contestant.is_verified :
        checker_results[0] = False
        checker_results[1].append("The second contestant is not verified")
    
    if not third_contestant.is_verified :
        checker_results[0] = False
        checker_results[1].append("The third contestant is not verified")
    
    return checker_results

def not_unique_users(first_contestant, second_contestant, third_contestant):
    return first_contestant == second_contestant or first_contestant == third_contestant or second_contestant == third_contestant

#######################################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ecpcq_register(request):
    
    if not ECPCQ.objects.exists() and ECPCQ.objects.exists().is_open():
        return Response({"Error" : "there is no ECPCQ registration"}, status.HTTP_400_BAD_REQUEST)
    
    ecpcq = ECPCQ.objects.first()
    first_contestant = request.user
    
    message = []
    
    try :
        second_contestant = User.objects.get(username=request.data.get('second_participant'))
    except :
        message.append("Invalid username for the second contestant")
    
    try :
        third_contestant = User.objects.get(username=request.data.get('third_participant'))
    except :
        message.append("Invalid username for the third contestant")
        
    if len(message) != 0 :
        return Response({"Error" : message}, status.HTTP_400_BAD_REQUEST)
    
    if not_unique_users(first_contestant, second_contestant, third_contestant) :
        return Response({"Error" : ["you can't register with the same user twice"]}, status.HTTP_400_BAD_REQUEST)
    
    there_coach, message = coach_included(first_contestant, second_contestant, third_contestant)
    if there_coach :
        return Response({"Error" : message}, status.HTTP_400_BAD_REQUEST)
    
    if not unregisters_users(first_contestant, second_contestant, third_contestant) :
        return Response({"Error" : ["one of the users is registered in another team"]}, status.HTTP_400_BAD_REQUEST)
    
    all_verified, message = all_users_virified(first_contestant, second_contestant, third_contestant)
    if not  all_verified:
        return Response({"Error" : message}, status.HTTP_400_BAD_REQUEST)
    
    team = Team.objects.create(team_name=request.data.get('team_name'))
    team.contestants.set([first_contestant, second_contestant, third_contestant])
    team.contest = ecpcq
    team.save()

    return Response({"Success" : "you have registered successfully"}, status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ecpcq_unregister(request) :
    if not ECPCQ.objects.exists() :
        return Response({"Error" : "There is no ECPCQ registration"}, status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    if not user.ecpcq_team.exists() :
        return Response({"Error" : "You are not registered in ECPCQ"}, status.HTTP_400_BAD_REQUEST)
    
    user.ecpcq_team.first().delete()

    return Response({"Success" : "You have unregistered"}, status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transportaion_register(request):
    if not Transportation.objects.exists() and Transportation.objects.first().is_open():
        return Response({"Error" : "There is no Transportation registration"}, status.HTTP_400_BAD_REQUEST)
    
    if not request.user.is_verified :
        return Response({"Error" : "You are not virified"}, status.HTTP_400_BAD_REQUEST)
    
    transportation = Transportation.objects.first()
    user = request.user
    transportation.users.add(user)
    transportation.save()
    return Response({"Success" : "You have registered successfully"}, status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transportaion_unregister(request):
    if not Transportation.objects.exists() :
        return Response({"Error" : "There is no Transportation registration"}, status.HTTP_400_BAD_REQUEST)
    
    transportation = Transportation.objects.first()
    user = request.user
    transportation.users.remove(user)
    transportation.save()
    return Response({"Success" : "You have unregistered"}, status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def housing_register(request):
    if not Housing.objects.exists() and Housing.objects.first().is_open():
        return Response({"Error" : "There is no Housing registration"}, status.HTTP_400_BAD_REQUEST)
    
    if not request.user.is_verified :
        return Response({"Error" : "You are not virified"}, status.HTTP_400_BAD_REQUEST)
    
    housing = Housing.objects.first()
    user = request.user
    housing.users.add(user)
    housing.save()
    return Response({"Success" : "You have registered successfully"}, status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def housing_unregister(request):
    if not Housing.objects.exists() :
        return Response({"Error" : "There is no Housing registration"}, status.HTTP_400_BAD_REQUEST)
    
    housing = Housing.objects.first()
    user = request.user
    housing.users.remove(user)
    housing.save()
    return Response({"Success" : "You have unregistered"}, status.HTTP_201_CREATED)