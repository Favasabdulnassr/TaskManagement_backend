from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
import random
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.db.models import Q
import logging
from datetime import datetime,timedelta
from .seriailizer import UserRegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .seriailizer import MyTokenObtainPairSerializer


logger = logging.getLogger(__name__)




User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():
            otp_register = serializer.validated_data['otp_register']
            recipient_mail = serializer.validated_data['email']

            request.session['registration_data'] = serializer.validated_data

            if otp_register:
                
                otp = str(random.randint(100000,999999))
                request.session['otp'] = otp

                expiration_time = datetime.now() + timedelta(minutes=2)
                request.session['otp_expiration'] = expiration_time.isoformat()

                
                request.session.save()


                
                # Send OTP via email for all users (both students and tutors)
                subject = 'Your 6 digit OTP for email verification'
                message = f"Your email verification OTP is {otp}"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [recipient_mail]
                
                try:
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    
                    return Response(
                        {
                            'message': 'OTP sent successfully to your email. Verify to complete registration',
                            'otp_expiration': expiration_time.isoformat(),
                            'session_id': request.session.session_key,
                        },
                        status=status.HTTP_201_CREATED
                    )
                except Exception as e:
                    return Response(
                        {'message': 'Failed to send OTP. Please try again.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                try:
                    serializer.save()
                    logger.info("User registered without OTP")
                    return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.exception("Error while saving user without OTP")  
                    return Response(
                        {
                            'message': 'Something went wrong while saving the user.',
                            'error': str(e)  
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        logger.error("Serializer errors", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]
    

    def post(self, request):

        otp = request.data.get('otp')
        session_otp = request.session.get('otp')
        session_id = request.data.get('sessionId')

        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()  # Decode the session data
        except Session.DoesNotExist:
            return Response({'error': 'Invalid session ID or session does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

         # Extract necessary data from the session

        session_otp = session_data.get('otp')
        registration_data = session_data.get('registration_data')
        otp_expiration = session_data.get('otp_expiration')


        # Check if session data exists
        if not session_otp or not registration_data or not otp_expiration:
            return Response(
                {'error': 'Session expired or no registration data found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP has expired
        current_time = datetime.now()
        expiration_time = datetime.fromisoformat(otp_expiration)  # Convert ISO format back to datetime
        if current_time > expiration_time:
            # Clear session data if expired
            session.delete()

            return Response(
                {'error': 'OTP has expired. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate OTP
        if otp == session_otp:
            # Create user and clear session
            registration_data.pop('confirm_password', None)
            registration_data.pop('otp_register',None)
            email = registration_data.get('email','')
            registration_data['username'] = email
            User.objects.create_user(**registration_data)
            session.delete()
            return Response({'message': 'Registration completed successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)




class MyTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("Request data:", request.data)  # 🪵 See incoming data
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("Error:", e)
            print("Serializer errors:", serializer.errors)
            return Response({"error": str(e), "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


from .seriailizer import UserSerializer

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request):
        serializer = UserSerializer(request.user,data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)