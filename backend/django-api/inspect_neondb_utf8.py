# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accused(models.Model):
    accusedmasterid = models.IntegerField(primary_key=True)
    casemasterid = models.ForeignKey('Casemaster', models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    accusedname = models.CharField(blank=True, null=True)
    ageyear = models.IntegerField(blank=True, null=True)
    genderid = models.IntegerField(blank=True, null=True)
    personid = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accused'


class Act(models.Model):
    actcode = models.CharField(primary_key=True)
    actdescription = models.CharField(blank=True, null=True)
    shortname = models.CharField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'act'


class Actsectionassociation(models.Model):
    casemasterid = models.ForeignKey('Casemaster', models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    actid = models.ForeignKey(Act, models.DO_NOTHING, db_column='actid', blank=True, null=True)
    sectionid = models.ForeignKey('Section', models.DO_NOTHING, db_column='sectionid', blank=True, null=True)
    actorderid = models.IntegerField(blank=True, null=True)
    sectionorderid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actsectionassociation'


class Arrestsurrender(models.Model):
    arrestsurrenderid = models.IntegerField(primary_key=True)
    casemasterid = models.ForeignKey('Casemaster', models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    arrestsurrendertypeid = models.IntegerField(blank=True, null=True)
    arrestsurrenderdate = models.DateField(blank=True, null=True)
    arrestsurrenderstateid = models.ForeignKey('State', models.DO_NOTHING, db_column='arrestsurrenderstateid', blank=True, null=True)
    arrestsurrenderdistrictid = models.ForeignKey('District', models.DO_NOTHING, db_column='arrestsurrenderdistrictid', blank=True, null=True)
    policestationid = models.ForeignKey('Unit', models.DO_NOTHING, db_column='policestationid', blank=True, null=True)
    ioid = models.ForeignKey('Employee', models.DO_NOTHING, db_column='ioid', blank=True, null=True)
    courtid = models.ForeignKey('Court', models.DO_NOTHING, db_column='courtid', blank=True, null=True)
    accusedmasterid = models.ForeignKey(Accused, models.DO_NOTHING, db_column='accusedmasterid', blank=True, null=True)
    isaccused = models.BooleanField(blank=True, null=True)
    iscomplainantaccused = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arrestsurrender'


class AuditAuditlog(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audit_auditlog'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class Casecategory(models.Model):
    casecategoryid = models.IntegerField(primary_key=True)
    lookupvalue = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casecategory'


class Casemaster(models.Model):
    casemasterid = models.IntegerField(primary_key=True)
    crimeno = models.CharField(blank=True, null=True)
    caseno = models.CharField(blank=True, null=True)
    crimeregistereddate = models.DateField(blank=True, null=True)
    policepersonid = models.ForeignKey('Employee', models.DO_NOTHING, db_column='policepersonid', blank=True, null=True)
    policestationid = models.ForeignKey('Unit', models.DO_NOTHING, db_column='policestationid', blank=True, null=True)
    casecategoryid = models.ForeignKey(Casecategory, models.DO_NOTHING, db_column='casecategoryid', blank=True, null=True)
    gravityoffenceid = models.ForeignKey('Gravityoffence', models.DO_NOTHING, db_column='gravityoffenceid', blank=True, null=True)
    crimemajorheadid = models.ForeignKey('Crimehead', models.DO_NOTHING, db_column='crimemajorheadid', blank=True, null=True)
    crimeminorheadid = models.ForeignKey('Crimesubhead', models.DO_NOTHING, db_column='crimeminorheadid', blank=True, null=True)
    casestatusid = models.ForeignKey('Casestatusmaster', models.DO_NOTHING, db_column='casestatusid', blank=True, null=True)
    courtid = models.ForeignKey('Court', models.DO_NOTHING, db_column='courtid', blank=True, null=True)
    incidentfromdate = models.DateTimeField(blank=True, null=True)
    incidenttodate = models.DateTimeField(blank=True, null=True)
    inforeceivedpsdate = models.DateTimeField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    longitude = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    brieffacts = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casemaster'


class Casestatusmaster(models.Model):
    casestatusid = models.IntegerField(primary_key=True)
    casestatusname = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casestatusmaster'


class Castemaster(models.Model):
    caste_master_id = models.IntegerField(primary_key=True)
    caste_master_name = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'castemaster'


class Chargesheetdetails(models.Model):
    csid = models.IntegerField(primary_key=True)
    casemasterid = models.ForeignKey(Casemaster, models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    csdate = models.DateTimeField(blank=True, null=True)
    cstype = models.CharField(max_length=1, blank=True, null=True)
    policepersonid = models.ForeignKey('Employee', models.DO_NOTHING, db_column='policepersonid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chargesheetdetails'


class Complainantdetails(models.Model):
    complainantid = models.IntegerField(primary_key=True)
    casemasterid = models.ForeignKey(Casemaster, models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    complainantname = models.CharField(blank=True, null=True)
    ageyear = models.IntegerField(blank=True, null=True)
    occupationid = models.ForeignKey('Occupationmaster', models.DO_NOTHING, db_column='occupationid', blank=True, null=True)
    religionid = models.ForeignKey('Religionmaster', models.DO_NOTHING, db_column='religionid', blank=True, null=True)
    casteid = models.ForeignKey(Castemaster, models.DO_NOTHING, db_column='casteid', blank=True, null=True)
    genderid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'complainantdetails'


class Court(models.Model):
    courtid = models.IntegerField(primary_key=True)
    courtname = models.CharField(blank=True, null=True)
    districtid = models.ForeignKey('District', models.DO_NOTHING, db_column='districtid', blank=True, null=True)
    stateid = models.ForeignKey('State', models.DO_NOTHING, db_column='stateid', blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'court'


class Crimehead(models.Model):
    crimeheadid = models.IntegerField(primary_key=True)
    crimegroupname = models.CharField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crimehead'


class Crimeheadactsection(models.Model):
    crimeheadid = models.ForeignKey(Crimehead, models.DO_NOTHING, db_column='crimeheadid', blank=True, null=True)
    actcode = models.ForeignKey(Act, models.DO_NOTHING, db_column='actcode', blank=True, null=True)
    sectioncode = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crimeheadactsection'


class Crimesubhead(models.Model):
    crimesubheadid = models.IntegerField(primary_key=True)
    crimeheadid = models.ForeignKey(Crimehead, models.DO_NOTHING, db_column='crimeheadid', blank=True, null=True)
    crimeheadname = models.CharField(blank=True, null=True)
    seqid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crimesubhead'


class Designation(models.Model):
    designationid = models.IntegerField(primary_key=True)
    designationname = models.CharField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    sortorder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'designation'


class District(models.Model):
    districtid = models.IntegerField(primary_key=True)
    districtname = models.CharField(blank=True, null=True)
    stateid = models.ForeignKey('State', models.DO_NOTHING, db_column='stateid', blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'district'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Employee(models.Model):
    employeeid = models.IntegerField(primary_key=True)
    districtid = models.ForeignKey(District, models.DO_NOTHING, db_column='districtid', blank=True, null=True)
    unitid = models.ForeignKey('Unit', models.DO_NOTHING, db_column='unitid', blank=True, null=True)
    rankid = models.ForeignKey('Rank', models.DO_NOTHING, db_column='rankid', blank=True, null=True)
    designationid = models.ForeignKey(Designation, models.DO_NOTHING, db_column='designationid', blank=True, null=True)
    kgid = models.CharField(blank=True, null=True)
    firstname = models.CharField(blank=True, null=True)
    employeedob = models.DateField(blank=True, null=True)
    genderid = models.IntegerField(blank=True, null=True)
    bloodgroupid = models.IntegerField(blank=True, null=True)
    physicallychallenged = models.BooleanField(blank=True, null=True)
    appointmentdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee'


class Gravityoffence(models.Model):
    gravityoffenceid = models.IntegerField(primary_key=True)
    lookupvalue = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gravityoffence'


class InvArrestsurrenderaccused(models.Model):
    arrestsurrenderid = models.ForeignKey(Arrestsurrender, models.DO_NOTHING, db_column='arrestsurrenderid', blank=True, null=True)
    accusedmasterid = models.ForeignKey(Accused, models.DO_NOTHING, db_column='accusedmasterid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inv_arrestsurrenderaccused'


class InvOccurancetime(models.Model):
    casemasterid = models.ForeignKey(Casemaster, models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inv_occurancetime'


class InvestigationInvestigationlog(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    entry_date_time = models.DateTimeField()
    notes = models.TextField()
    fir_id = models.UUIDField()
    recorded_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'investigation_investigationlog'


class Occupationmaster(models.Model):
    occupationid = models.IntegerField(primary_key=True)
    occupationname = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'occupationmaster'


class Rank(models.Model):
    rankid = models.IntegerField(primary_key=True)
    rankname = models.CharField(blank=True, null=True)
    hierarchy = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rank'


class Religionmaster(models.Model):
    religionid = models.IntegerField(primary_key=True)
    religionname = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'religionmaster'


class Section(models.Model):
    sectioncode = models.CharField(primary_key=True)
    actcode = models.ForeignKey(Act, models.DO_NOTHING, db_column='actcode', blank=True, null=True)
    sectiondescription = models.CharField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section'


class State(models.Model):
    stateid = models.IntegerField(primary_key=True)
    statename = models.CharField(blank=True, null=True)
    nationalityid = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'state'


class Unit(models.Model):
    unitid = models.IntegerField(primary_key=True)
    unitname = models.CharField(blank=True, null=True)
    typeid = models.ForeignKey('Unittype', models.DO_NOTHING, db_column='typeid', blank=True, null=True)
    parentunit = models.IntegerField(blank=True, null=True)
    nationalityid = models.IntegerField(blank=True, null=True)
    stateid = models.ForeignKey(State, models.DO_NOTHING, db_column='stateid', blank=True, null=True)
    districtid = models.ForeignKey(District, models.DO_NOTHING, db_column='districtid', blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unit'


class Unittype(models.Model):
    unittypeid = models.IntegerField(primary_key=True)
    unittypename = models.CharField(blank=True, null=True)
    citydiststate = models.CharField(blank=True, null=True)
    hierarchy = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unittype'


class UsersUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    role = models.CharField(max_length=20)
    badge_number = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_groups'
        unique_together = (('user', 'group'),)


class UsersUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Victim(models.Model):
    victimmasterid = models.IntegerField(primary_key=True)
    casemasterid = models.ForeignKey(Casemaster, models.DO_NOTHING, db_column='casemasterid', blank=True, null=True)
    victimname = models.CharField(blank=True, null=True)
    ageyear = models.IntegerField(blank=True, null=True)
    genderid = models.IntegerField(blank=True, null=True)
    victimpolice = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'victim'
