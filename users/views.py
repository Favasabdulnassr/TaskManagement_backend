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

    def post(self, request):
        logger.info("Register endpoint called")
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            logger.info("Serializer valid")
            otp_register = serializer.validated_data['otp_register']
            recipient_mail = serializer.validated_data['email']
            request.session['registration_data'] = serializer.validated_data

            if otp_register:
                try:
                    otp = str(random.randint(100000, 999999))
                    request.session['otp'] = otp
                    expiration_time = datetime.now() + timedelta(minutes=2)
                    request.session['otp_expiration'] = expiration_time.isoformat()
                    request.session.save()

                    subject = 'Your 6 digit OTP for email verification'
                    message = f"Your email verification OTP is {otp}"
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [recipient_mail]

                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                    logger.info(f"OTP {otp} sent to {recipient_mail}")

                    return Response(
                        {
                            'message': 'OTP sent successfully to your email. Verify to complete registration',
                            'otp_expiration': expiration_time.isoformat(),
                            'session_id': request.session.session_key,
                        },
                        status=status.HTTP_201_CREATED
                    )

                except Exception as e:
                    logger.exception("Failed to send OTP or session error")
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


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ResendOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Resend OTP endpoint called")

        session_id = request.data.get('sessionId')
        logger.info(f"Session ID received from request: {session_id}")

        if not session_id:
            logger.error("Session ID is missing in the request")
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(session_key=session_id)
            logger.info("Session object retrieved successfully")
            session_data = session.get_decoded()
            logger.info(f"Session data decoded: {session_data}")
        except Session.DoesNotExist:
            logger.error("Invalid session ID. Session does not exist.")
            return Response({'error': 'Invalid session ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Get email and registration data
        registration_data = session_data.get('registration_data')
        logger.info(f"Registration data extracted from session: {registration_data}")

        if not registration_data:
            logger.error("No registration data found in session")
            return Response({'error': 'No registration data found in session'}, status=status.HTTP_400_BAD_REQUEST)

        recipient_mail = registration_data.get('email')
        logger.info(f"Recipient email extracted: {recipient_mail}")

        if not recipient_mail:
            logger.error("Email not found in session registration data")
            return Response({'error': 'Email not found in session data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate new OTP
            new_otp = str(random.randint(100000, 999999))
            logger.info(f"Generated new OTP: {new_otp}")

            expiration_time = datetime.now() + timedelta(minutes=2)
            logger.info(f"New OTP expiration time: {expiration_time}")

            # Update session with new OTP
            session_data['otp'] = new_otp
            session_data['otp_expiration'] = expiration_time.isoformat()
            session.session_data = Session.objects.encode(session_data)
            session.save()
            logger.info("Session updated with new OTP and expiration time")

            # Send the new OTP email
            subject = 'Resent OTP for Email Verification'
            message = f"Your new OTP is {new_otp}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [recipient_mail]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.info(f"Sent OTP email to {recipient_mail}")

            return Response(
                {
                    'message': 'OTP resent successfully.',
                    'otp_expiration': expiration_time.isoformat()
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception("Error while resending OTP")
            return Response(
                {'error': 'Failed to resend OTP. Please try again.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )






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