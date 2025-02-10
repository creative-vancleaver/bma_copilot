from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Super user must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Super user must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    user_id = models.CharField(primary_key=True, max_length=255)  # Match Azure's user_id

    email = models.EmailField(unique=True, max_length=250)
    username = None
    institution = models.CharField(max_length=250, blank=True, null=True)
    password = models.CharField(max_length=128)  # Ensure it exists in SQL
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'  # Ensure correct table mapping

    USERNAME_FIELD = 'email' # USER EMAIL FOR AUTH
    REQUIRED_FIELDS = [] # REMOVE USERNAME FROM REQUIRED FIELDS

    objects = CustomUserManager()

    class Meta:
        app_label = 'users'
        db_table = 'users'  # Match Azure table name
        # # managd = False