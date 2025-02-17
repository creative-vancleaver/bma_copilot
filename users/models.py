import uuid
import re
from django.db import models
from django.db.models import Max
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('user_id', self.generate_user_id())
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        extra_fields.setdefault('user_id', self.generate_user_id())

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Super user must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Super user must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)
    
    def generate_user_id(self):
        last_user = self.model.objects.order_by('-user_id').first()
        if last_user and last_user.user_id.isdigit():
            return str(int(last_user.user_id) + 1)
        return "1"

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

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.objects.generate_user_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} (ID: {self.user_id})"

    class Meta:
        app_label = 'users'
        db_table = 'users'  # Match Azure table name
        # # managed = False







class CustomIDMixin(models.Model):

    @classmethod
    def generate_custom_id(cls, **kwargs):
        """
        Generates a hierarchical custom ID while ensuring numeric sorting.
        """
        if cls:
            primary_key_field = cls._meta.pk.name
            
            def extract_last_number(value):
                numbers = re.findall(r'\d+', value)
                return int(numbers[-1]) if numbers else 0

            key_components = [str(value) for key, value in kwargs.items() if value is not None]

            existing_ids = cls.objects.filter(**kwargs).values_list(primary_key_field, flat=True)

            last_numeric_id = max([extract_last_number(id_str) for id_str in existing_ids], default=0)

            next_id = str(last_numeric_id + 1)

            new_id = "_".join(key_components + [next_id])

            print(f"[DEBUG] Generated ID: {new_id}")  # Debugging print statement

            return new_id
        
    class Meta:
        abstract = True
