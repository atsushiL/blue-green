import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# システムユーザ
class User(AbstractUser):
    # ロールのenum
    class Role(models.IntegerChoices):
        MANAGEMENT = 0
        GENERAL = 1
        SALES = 2

    first_name = None
    last_name = None
    date_joined = None
    groups = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        error_messages={"unique": "その社員番号のユーザはすでに登録されています。"},
        help_text="半角英数字8文字の社員番号を入力してください。",
        max_length=8,
        unique=True,
        validators=[RegexValidator(r"^[0-9]{8}$", "8桁の数字を入力してください。")],
        verbose_name="社員番号",
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    role = models.PositiveIntegerField(choices=Role.choices, default=Role.SALES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    mail_sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "User"
        constraints = [
            models.UniqueConstraint(fields=["id", "username"], name="unique_user")
        ]

    def __str__(self):
        return self.username


# お客様
class Customer(models.Model):
    class Entrance(models.IntegerChoices):
        PROSPECT = 0
        PROVISIONAL = 1

    class CustomerStatus(models.IntegerChoices):
        PROSPECT = 0
        PROVISIONAL = 1
        FINAL = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entrance = models.PositiveSmallIntegerField(
        choices=Entrance.choices,
        default=Entrance.PROSPECT,
        null=True,
        blank=True,
    )
    customer_status = models.PositiveSmallIntegerField(
        choices=CustomerStatus.choices, default=CustomerStatus.PROSPECT
    )
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="customer_status_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="customer_status_updated_by"
    )

    class Meta:
        db_table = "Customer"


# お客様情報
class CustomerData(models.Model):
    # 性別のenum
    class Sex(models.IntegerChoices):
        MALE = 0
        FEMALE = 1
        OTHER = 2
        NOT_ENTERED = 3

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="customer_data"
    )
    name = models.CharField(max_length=60)
    kana = models.CharField(max_length=60)
    birthday = models.DateField()
    sex = models.PositiveSmallIntegerField(choices=Sex.choices, default=Sex.NOT_ENTERED)
    email = models.EmailField()
    memo = models.CharField(max_length=255, null=True, blank=True, default="")
    cellphone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10桁か11桁の数字を入力してください。")],
        null=True,
        blank=True,
    )
    # 携帯の電話番号優先
    phone_no = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^[0-9]{10}$", "10桁の数字を入力してください。")],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "CustomerData"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


# 住所
class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        "Estate", on_delete=models.CASCADE, related_name="address", null=True
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="address", null=True
    )
    land = models.ForeignKey(
        "Land", on_delete=models.CASCADE, related_name="address", null=True
    )
    prefecture = models.CharField(max_length=255, null=True)
    municipalities = models.CharField(max_length=255)
    house_no = models.CharField(max_length=255)
    post_no = models.CharField(
        max_length=7, validators=[RegexValidator(r"^[0-9]{7}$", "7桁の数字を入力してください。")]
    )
    other = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def update(self, **kwargs):
        self.clean()
        return super(Address, self).update(**kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Address, self).save(*args, **kwargs)

    def clean(self):
        # この中で1つだけAddressに紐づいていれば通ります。2つ以上紐づいていると失敗します。
        count = [bool(self.estate), bool(self.customer), bool(self.land)].count(True)
        if count != 1:
            raise ValidationError("住所はどれか一つのテーブルに繋げてください。複数のテーブルと1つの住所が紐づくことはできません。")
        return super().clean()

    class Meta:
        db_table = "Address"
        ordering = ("-created_at",)


# 契約
class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    final_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Contract"


# 契約データ
class ContractData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    contract_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ContractData"


# 見込客
class ProspectCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="prospect_customer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ProspectCustomer"


# 見込客データ
class ProspectCustomerData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prospect_customer = models.ForeignKey(
        ProspectCustomer,
        on_delete=models.CASCADE,
        related_name="prospect_customer_data",
    )
    prefecture = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ProspectCustomerData"


# 仮申込客
class ProvisionalCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="provisional_customer"
    )
    introduction_company = models.ForeignKey(
        "IntroductionCompany",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="introduced_provisional_customer",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ProvisionalCustomer"


# 仮申込データ
class ProvisionalCustomerData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer,
        on_delete=models.CASCADE,
        related_name="provisional_customer_data",
    )

    # 仮申込ステータスのenum
    class Status(models.IntegerChoices):
        UNTOUCHED = 0
        IN_PROGRESS = 1
        INTERNAL_APPROVAL = 2
        CUSTOMER_APPROVAL = 3
        RENEGOTIATION = 4
        WITHDRAWAL = 5
        PROCESSED = 6

    class Property(models.IntegerChoices):
        INDIVIDUAL = 0
        LEGAL_ENTITY = 1

    application_date = models.DateField()
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.UNTOUCHED,
    )
    property = models.PositiveSmallIntegerField(
        choices=Property.choices,
        default=Property.INDIVIDUAL,
    )
    approval = models.BooleanField(null=True, blank=True, default=None)
    reason_for_refusal = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ProvisionalCustomerData"
        ordering = ("-created_at",)


# 仮申込客反社チェックデータ
class AntiSocialCheckResult(models.Model):
    class ANTI_SOCIAL_CHECK(models.IntegerChoices):
        UNTOUCHED = 0
        WAITING_FOR_RESULT = 1
        RESULTS_REGISTERED = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer,
        on_delete=models.CASCADE,
        related_name="anti_social_check_result",
    )
    anti_social_check_status = models.PositiveSmallIntegerField(
        choices=ANTI_SOCIAL_CHECK.choices,
        default=ANTI_SOCIAL_CHECK.UNTOUCHED,
    )
    anti_social_result = models.BooleanField(
        default=None,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "AntiSocialCheckResult"
        ordering = ("-created_at",)


# 申込情報
class ApplicationInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE, related_name="application_info"
    )
    preferred_rent_fee = models.PositiveIntegerField(default=0)
    preferred_purchase_fee = models.PositiveIntegerField(default=0)
    how_to_know = models.CharField(max_length=255)
    assumed_years_of_residence = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ApplicationInfo"
        ordering = ("-created_at",)


# 本申込客
class FinalCustomer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FinalCustomer"


# 本申込客データ
class FinalCustomerData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    final_customer = models.ForeignKey(FinalCustomer, on_delete=models.CASCADE)
    emergency_contact_kana = models.CharField(max_length=255)
    emergency_contact = models.CharField(max_length=255)
    emergency_phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10桁か11桁の数字を入力してください。")],
    )
    requests = models.TextField(null=True, blank=True)
    insurance_company = models.ForeignKey(
        "InsuranceCompany", on_delete=models.DO_NOTHING
    )
    guarantee_company = models.ForeignKey(
        "GuaranteeCompany", on_delete=models.DO_NOTHING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FinalCustomerData"


# 勤務先
class WorkplaceInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )
    industry = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    # 年収(万円単位)
    annual_income = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="workplace"
    )

    class Meta:
        db_table = "WorkplaceInfo"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


# 販促方法
class PromotionMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="promotion_method"
    )
    method = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PromotionMethod"

    def __str__(self):
        return self.method


# 販促結果
class PromotionResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="promotion_result"
    )

    class Meta:
        db_table = "PromotionResult"

    def __str__(self):
        return self.result


# 見込客交渉履歴
class CustomerNegotiationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="negotiation_history"
    )
    promotion_method = models.ForeignKey(
        PromotionMethod, on_delete=models.DO_NOTHING, related_name="negotiation_history"
    )
    result = models.ForeignKey(PromotionResult, on_delete=models.DO_NOTHING)
    conversation = models.TextField(null=True, blank=True)
    negotiation_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="negotiation_history_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="negotiation_history_updated_by"
    )

    class Meta:
        db_table = "CustomerNegotiationHistory"
        ordering = ("-created_at",)


# ヒアリング項目
class InterviewItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.CharField(max_length=255)
    memo = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="interview_item"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "InterviewItem"

    def __str__(self):
        return self.item


# ヒアリング
class Interview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview_item = models.ForeignKey(InterviewItem, on_delete=models.DO_NOTHING)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    interview_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Interview"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["provisional_customer", "interview_item"],
                name="interview_item_unique",
            ),
        ]

    def __str__(self):
        return self.interview


class InterviewHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    interview_item = models.ForeignKey(InterviewItem, on_delete=models.DO_NOTHING)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    interview_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "InterviewHistory"
        ordering = ("-created_at",)

    def __str__(self):
        return self.interview


# 家族
class Family(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    relationship = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()
    job = models.CharField(max_length=255)
    household_management = models.BooleanField(default=False)
    consensus = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Family"


# ローン
class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    remaining_housing_loan_debt = models.PositiveIntegerField(default=0)
    monthly_repayment = models.PositiveIntegerField(default=0)
    bonus_month_repayment = models.PositiveIntegerField(default=0)
    arrear = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Loan"
        ordering = ("-created_at",)


# 銀行口座
class BankAccount(models.Model):
    # 口座種別のenum
    class AccountType(models.IntegerChoices):
        ORDINARY = 0
        CURRENT = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provisional_customer = models.ForeignKey(
        ProvisionalCustomer, on_delete=models.CASCADE
    )
    number = models.CharField(
        max_length=7, validators=[RegexValidator(r"^[0-9]{7}$", "7桁の数字を入力してください。")]
    )
    holder = models.CharField(max_length=255)
    account_type = models.PositiveSmallIntegerField(
        choices=AccountType.choices, default=AccountType.ORDINARY
    )
    bank = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "BankAccount"
        ordering = ("-created_at",)

    def __str__(self):
        return self.number


# メール
class Mail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    send_datetime = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        db_table = "Mail"

    def __str__(self):
        return self.subject


# 土地
class Land(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="land_created_by"
    )

    class Meta:
        db_table = "Land"


# 土地データ
class LandData(models.Model):
    class LandMark(models.IntegerChoices):
        BUILDING_LOT = 0
        RICE_FIELD = 1
        FIELD = 2
        FOREST = 3
        HYBRID = 4

    class HolderType(models.IntegerChoices):
        SELF = 0
        NO_HOLDER = 1
        SHARE = 2

    class LandMark(models.IntegerChoices):
        BUILDING_LOT = 0
        RICE_FIELD = 1
        FIELD = 2
        FOREST = 3
        HYBRID = 4

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name="land_data")
    registered_size_square = models.DecimalField(max_digits=6, decimal_places=2)
    lot_no = models.CharField(max_length=30)
    landmark = models.PositiveIntegerField(
        choices=LandMark.choices, default=LandMark.BUILDING_LOT
    )
    holder = models.CharField(max_length=255, null=True)
    holder_type = models.PositiveSmallIntegerField(
        choices=HolderType.choices, default=HolderType.SELF, null=True
    )
    property_tax = models.PositiveIntegerField(default=0, null=True)
    property_tax_pay_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="land_data_created_by"
    )

    class Meta:
        db_table = "LandData"


# 土地の登記簿謄本
class LandCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    land = models.ForeignKey(
        Land, on_delete=models.CASCADE, related_name="land_certificate"
    )
    photo = models.CharField(max_length=2083)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="land_certificate_created_by"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "LandCertificate"


# 土地の画像
class LandPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    photo = models.CharField(max_length=2083)
    memo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "LandPhoto"


# 保証会社
class GuaranteeCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "GuaranteeCompany"

    def __str__(self):
        return self.name


# 物件
class Estate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="estate"
    )
    # 保証会社は二次開発にやります。
    # guarantee_company = models.ForeignKey(GuaranteeCompany, on_delete=models.DO_NOTHING)
    introduction_company = models.ForeignKey(
        "IntroductionCompany",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="estate_created_by"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="estate_updated_by"
    )

    class Meta:
        db_table = "Estate"


# 物件の情報
class BuildingInfo(models.Model):
    # 物件種別のenum
    class Category(models.IntegerChoices):
        HOUSE = 0
        APARTMENT = 1

    class HolderType(models.IntegerChoices):
        SELF = 0
        NO_HOLDER = 1
        SHARE = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="building_info"
    )
    category = models.PositiveIntegerField(
        choices=Category.choices, default=Category.HOUSE
    )
    attachment_count = models.PositiveSmallIntegerField(default=0)
    mortgage_count = models.PositiveSmallIntegerField(default=0)
    reform = models.BooleanField()
    footprint = models.DecimalField(max_digits=6, decimal_places=2)
    footprint_rate = models.DecimalField(max_digits=6, decimal_places=2)
    cancellation_fee = models.PositiveIntegerField(default=0)
    management_fee = models.PositiveIntegerField(default=0)
    age = models.PositiveSmallIntegerField()
    direction = models.CharField(max_length=20)
    front_road = models.DecimalField(max_digits=6, decimal_places=2)
    nearest_station = models.CharField(max_length=255, null=True)
    house_no = models.CharField(max_length=255, null=True)
    holder = models.CharField(max_length=255, null=True)
    holder_type = models.PositiveSmallIntegerField(
        choices=HolderType.choices, default=HolderType.SELF, null=True
    )
    fire_insurance_fee = models.PositiveIntegerField(default=0, null=True)
    fire_insurance_renewal_date = models.DateTimeField(null=True)
    property_tax = models.PositiveIntegerField(default=0, null=True)
    property_tax_pay_date = models.DateTimeField(null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "BuildingInfo"


# 管理会社
class ManagementCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )

    class Meta:
        db_table = "ManagementCompany"

    def __str__(self):
        return self.name


# 管理会社費用
class ManagementCompanyExpense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(ManagementCompany, on_delete=models.CASCADE)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    consignment_fee = models.PositiveIntegerField(default=0)
    union_fee = models.PositiveIntegerField(default=0)
    deposit_fee = models.PositiveIntegerField(default=0)
    renewal_fee = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ManagementCompanyExpense"


# 不動産の登記簿謄本
class EstateCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="estate_certificate"
    )
    photo = models.CharField(max_length=2083)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EstateCertificate"


# 家賃,入金管理
class RentFee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    final_customer = models.ForeignKey(FinalCustomer, on_delete=models.CASCADE)
    fee = models.PositiveIntegerField(default=0)
    payment = models.BooleanField(default=False)
    payment_day = models.DateField()
    arrear = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "RentFee"


# 保険会社
class InsuranceCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ManyToManyField(Estate)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "InsuranceCompany"

    def __str__(self):
        return self.name


# 紹介会社
class IntroductionCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )
    person_in_charge = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="introduction_company_created_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="introduction_company_updated_by",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "IntroductionCompany"

    def __str__(self):
        return self.name


# 甲区
class Kouku(models.Model):
    # 目的
    class Purpose(models.IntegerChoices):
        OWNERSHIP = 0
        ATTACHMENT = 1

    # 理由
    class Reason(models.IntegerChoices):
        SALE = 0
        DESCENT = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, null=True, related_name="kouku"
    )
    land = models.ForeignKey(
        Land, on_delete=models.CASCADE, null=True, related_name="kouku"
    )
    purpose = models.PositiveIntegerField(
        choices=Purpose.choices, default=Purpose.OWNERSHIP
    )
    reception_date = models.DateField(auto_now_add=True)
    reason = models.PositiveIntegerField(choices=Reason.choices, default=Reason.SALE)
    holder = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="kouku_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="kouku_updated_by"
    )

    def update(self, **kwargs):
        self.clean()
        return super(Kouku, self).update(**kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Kouku, self).save(*args, **kwargs)

    def clean(self):
        # この中で1つだけに紐づいていれば通ります。2つ以上紐づいていると失敗します。
        count = [bool(self.estate), bool(self.land)].count(True)
        if count != 1:
            raise ValidationError("甲区は一つのテーブルに繋げてください。複数のテーブルと1つの甲区が紐づくことはできません。")
        return super().clean()

    class Meta:
        db_table = "Kouku"

    def __str__(self):
        return self.holder


# 乙区
class Otsuku(models.Model):
    # 目的
    class Purpose(models.IntegerChoices):
        MORTGAGE = 0
        REVOLVING_MORTGAGE = 1

    # 債権者
    class Debtee(models.IntegerChoices):
        MORTGAGEE = 0
        REVOLVING_MORTGAGEE = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, null=True, related_name="otsuku"
    )
    land = models.ForeignKey(
        Land, on_delete=models.CASCADE, null=True, related_name="otsuku"
    )
    purpose = models.PositiveIntegerField(
        choices=Purpose.choices, default=Purpose.MORTGAGE
    )
    reception_date = models.DateField(auto_now_add=True)
    loan = models.PositiveIntegerField(default=0)
    debtor = models.CharField(max_length=255)
    debtee = models.PositiveIntegerField(
        choices=Debtee.choices, default=Debtee.MORTGAGEE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="otsuku_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="otsuku_updated_by"
    )

    def update(self, **kwargs):
        self.clean()
        return super(Otsuku, self).update(**kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Otsuku, self).save(*args, **kwargs)

    def clean(self):
        # この中で1つだけに紐づいていれば通ります。2つ以上紐づいていると失敗します。
        count = [bool(self.estate), bool(self.land)].count(True)
        if count != 1:
            raise ValidationError("乙区は一つのテーブルに繋げてください。複数のテーブルと1つの乙区が紐づくことはできません。")
        return super().clean()

    class Meta:
        db_table = "Otsuku"

    def __str__(self):
        return self.debtor


# 修理会社
class RepairCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )

    class Meta:
        db_table = "RepairCompany"

    def __str__(self):
        return self.name


# 修理
class Repair(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    repair_company = models.ForeignKey(RepairCompany, on_delete=models.DO_NOTHING)
    repair_info = models.CharField(max_length=255)
    repair_fee = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="repair_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="repair_updated_by"
    )

    class Meta:
        db_table = "Repair"


# 基準マスタ
class EvaluationStandard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard = models.CharField(max_length=255)
    standard_content = models.CharField(max_length=255)
    memo = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EvaluationStandard"

    def __str__(self):
        return self.standard


# 物件の評価結果
class EvaluationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation_standard = models.ForeignKey(
        EvaluationStandard,
        on_delete=models.DO_NOTHING,
        related_name="evaluation_result",
    )
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, related_name="evaluation_result"
    )
    result = models.TextField()
    evaluation_judge = models.BooleanField(blank=True, null=True, default=None)
    reason_memo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="evaluation_result_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="evaluation_result_updated_by"
    )

    class Meta:
        db_table = "EvaluationResult"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["estate", "evaluation_standard"],
                name="evaluation_standard_unique",
            ),
        ]


# 評価会社
class EvaluateCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^[0-9]{10,11}$", "10か11桁の数字を入力してください。")],
    )
    memo = models.TextField(null=True, blank=True)
    person_in_charge = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "EvaluateCompany"

    def __str__(self):
        return self.name


# 評価会社の評価
class EvaluateCompanyEvaluations(models.Model):
    # 進捗状況のenum
    class Status(models.IntegerChoices):
        UNTOUCHED = 0
        IN_PROGRESS = 1
        COMPLETE = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name="evaluate_company_evaluations",
    )
    evaluate_company = models.ForeignKey(
        EvaluateCompany,
        on_delete=models.CASCADE,
        related_name="evaluate_company_evaluations",
    )
    estate_valuation_fee = models.PositiveIntegerField(default=0)
    land_valuation_fee = models.PositiveIntegerField(default=0)
    memo = models.TextField(null=True, blank=True, default="")
    status = models.PositiveIntegerField(
        choices=Status.choices, default=Status.UNTOUCHED
    )
    memo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluation_company_evaluations_created_by",
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluation_company_evaluations_updated_by",
    )

    class Meta:
        db_table = "EvaluateCompanyEvaluations"


# 物件画像
class EstatePhoto(models.Model):
    # 物件が内か外かのenum
    class INOUT(models.IntegerChoices):
        IN = 0
        OUT = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    photo = models.CharField(max_length=2083)
    memo = models.TextField(null=True, blank=True)
    in_out = models.PositiveIntegerField(choices=INOUT.choices, default=INOUT.IN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EstatePhoto"


# ペット
class Pet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="pet")
    type = models.CharField(max_length=255)
    count = models.PositiveSmallIntegerField(default=0)
    environment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Pet"


class EarningsSim(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE)
    earnings_sim_photo = models.ImageField(upload_to="earnings_sim")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "EarningsSim"
        ordering = ("-created_at",)


# 収益sim
class EarningsIndex(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sim = models.ForeignKey(EarningsSim, on_delete=models.CASCADE)
    land_valuation = models.DecimalField(max_digits=6, decimal_places=2)
    estate_valuation = models.DecimalField(max_digits=6, decimal_places=2)
    land_acquisition_tax = models.DecimalField(max_digits=6, decimal_places=2)
    estate_acquisition_tax = models.DecimalField(max_digits=6, decimal_places=2)
    land_registration_license_tax = models.DecimalField(max_digits=6, decimal_places=2)
    estate_registration_license_tax = models.DecimalField(
        max_digits=6, decimal_places=2
    )
    intermediate_fee = models.PositiveIntegerField(default=0)
    related_fee = models.PositiveIntegerField(default=0)
    sales_tax_rate = models.DecimalField(max_digits=6, decimal_places=2)
    judicial_scrivener_fee = models.DecimalField(max_digits=6, decimal_places=1)
    consignment_fee = models.PositiveIntegerField(default=0)
    monthly_management_repair_fund = models.PositiveIntegerField(default=0)
    property_tax_index = models.DecimalField(max_digits=6, decimal_places=2)
    city_planning_tax = models.DecimalField(max_digits=6, decimal_places=2)
    fire_insurance_fee = models.PositiveIntegerField(default=0)
    fire_insurance_renewal_date = models.DateField()
    other_fee = models.PositiveIntegerField(default=0)
    renewal_fee = models.PositiveIntegerField(default=0)
    estate_sell_off = models.DecimalField(max_digits=6, decimal_places=2)
    property_tax_pay_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "EarningsIndex"


class ALBAntiSocialCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=60)
    kana = models.CharField(max_length=60)
    birthday = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=255, blank=True)
    cellphone_no = models.CharField(max_length=255, blank=True)
    workplace = models.CharField(max_length=255, blank=True)
    workplace_phone_no = models.CharField(max_length=255, blank=True)
    account_overview = models.CharField(max_length=255, blank=True)
    balance = models.CharField(max_length=255, blank=True)
    new_appraisal_loan_date = models.CharField(max_length=255, blank=True)
    exclusion_clause = models.CharField(max_length=255)
    anti_social_confirmation_date = models.CharField(max_length=255, blank=True)
    anti_social_confirmation_reason = models.TextField(blank=True)
    response_policy = models.TextField(blank=True)
    receipt_date = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "ALBAntiSocialCheck"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "kana",
                    "birthday",
                    "address",
                ],
                name="ALBAntiSocialCheck_unique",
            ),
        ]


class PurchaseSurvey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estate = models.ForeignKey(
        "Estate",
        on_delete=models.CASCADE,
        related_name="purchase_survey",
        null=True,
    )
    purchase_date = models.DateField(null=True)
    purchase_price = models.PositiveIntegerField(default=0)
    result = models.BooleanField(null=True, blank=True, default=None)
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "PurchaseSurvey"
        ordering = ("-created_at",)
