from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime
from django.db.models import Sum
from decimal import Decimal

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    profesion = models.CharField(max_length=100, blank=True)
    salario_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def saldo_disponible(self):
        # Calcular gastos solo del mes actual
        now = datetime.now()
        mes_actual = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_gastos_mes = self.user.gasto_set.filter(
            fecha__gte=mes_actual
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
        
        return self.salario_mensual - total_gastos_mes
    
    def get_gastos_mes_actual(self):
        """Obtiene los gastos del mes actual"""
        now = datetime.now()
        mes_actual = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return self.user.gasto_set.filter(
            fecha__gte=mes_actual
        )
    
    def get_total_gastos_mes(self):
        """Obtiene el total de gastos del mes actual"""
        return self.get_gastos_mes_actual().aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0')

class Gasto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    fecha = models.DateTimeField(auto_now_add=True)
    imagen_comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.descripcion} - ${self.monto}"

class GastoFijo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['descripcion']
    
    def __str__(self):
        return f"{self.descripcion} - ${self.monto} (Fijo)"
    
    def aplicar_gasto(self):
        """Crea un gasto regular a partir de este gasto fijo"""
        return Gasto.objects.create(
            usuario=self.usuario,
            descripcion=self.descripcion,
            monto=self.monto
        )

class Vencimiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, help_text="Descripción del vencimiento (ej: Pago de tarjeta, Renovación de seguro)")
    fecha_vencimiento = models.DateField(help_text="Fecha en que vence")
    activo = models.BooleanField(default=True, help_text="Si está activo, se mostrarán las advertencias")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_vencimiento']
        verbose_name = 'Vencimiento'
        verbose_name_plural = 'Vencimientos'
    
    def __str__(self):
        return f"{self.descripcion} - {self.fecha_vencimiento.strftime('%d/%m/%Y')}"
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes hasta el vencimiento"""
        from datetime import date
        hoy = date.today()
        delta = self.fecha_vencimiento - hoy
        return delta.days
    
    @property
    def esta_proximo(self):
        """Verifica si el vencimiento está dentro de los próximos 3 días"""
        return 0 <= self.dias_restantes <= 3
    
    @property
    def esta_vencido(self):
        """Verifica si ya está vencido"""
        return self.dias_restantes < 0



class MetaAhorro(models.Model):
    """Modelo para metas de ahorro del usuario"""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('completada', 'Completada'),
        ('pausada', 'Pausada'),
        ('cancelada', 'Cancelada'),
    ]
    
    ICONO_CHOICES = [
        ('piggy-bank', '🐷 Alcancía'),
        ('car', '🚗 Auto'),
        ('plane', '✈️ Viaje'),
        ('home', '🏠 Casa'),
        ('graduation-cap', '🎓 Educación'),
        ('ring', '💍 Boda'),
        ('baby', '👶 Bebé'),
        ('laptop', '💻 Tecnología'),
        ('bicycle', '🚲 Bicicleta'),
        ('camera', '📷 Cámara'),
        ('gamepad', '🎮 Videojuegos'),
        ('music', '🎵 Música'),
        ('gift', '🎁 Regalo'),
        ('heart', '❤️ Salud'),
        ('star', '⭐ Sueño'),
    ]
    
    COLOR_CHOICES = [
        ('primary', 'Azul'),
        ('success', 'Verde'),
        ('info', 'Celeste'),
        ('warning', 'Amarillo'),
        ('danger', 'Rojo'),
        ('secondary', 'Gris'),
        ('dark', 'Negro'),
        ('purple', 'Morado'),
        ('pink', 'Rosa'),
        ('orange', 'Naranja'),
    ]
    
    MONEDA_CHOICES = [
        ('ARS', 'Pesos Argentinos (ARS)'),
        ('USD', 'Dólares Estadounidenses (USD)'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, help_text="Nombre de la meta (ej: Viaje a Europa, Auto nuevo)")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada de la meta")
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)], help_text="Monto total a ahorrar")
    monto_ahorrado = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], help_text="Monto ya ahorrado")
    fecha_objetivo = models.DateField(help_text="Fecha límite para alcanzar la meta")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    icono = models.CharField(max_length=50, choices=ICONO_CHOICES, default='piggy-bank', help_text="Ícono de la meta")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='primary', help_text="Color del tema (Bootstrap)")
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='ARS', help_text="Moneda del objetivo")
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Meta de Ahorro'
        verbose_name_plural = 'Metas de Ahorro'
    
    def __str__(self):
        return f"{self.nombre} - ${self.monto_objetivo}"
    
    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de la meta completado"""
        if self.monto_objetivo > 0:
            from decimal import Decimal
            return min((self.monto_ahorrado / self.monto_objetivo) * Decimal('100'), Decimal('100'))
        return 0
    
    @property
    def monto_restante(self):
        """Calcula cuánto falta para completar la meta"""
        return max(self.monto_objetivo - self.monto_ahorrado, 0)
    
    @property
    def dias_restantes(self):
        """Calcula cuántos días quedan para la fecha objetivo"""
        from datetime import date
        if self.fecha_objetivo > date.today():
            return (self.fecha_objetivo - date.today()).days
        return 0
    
    @property
    def ahorro_mensual_recomendado(self):
        """Calcula cuánto se debe ahorrar por mes para alcanzar la meta"""
        if self.dias_restantes <= 0:
            return self.monto_restante
        
        from decimal import Decimal
        meses_restantes = max(Decimal(str(self.dias_restantes)) / Decimal('30.44'), Decimal('1'))  # 30.44 días promedio por mes
        return self.monto_restante / meses_restantes
    
    @property
    def ahorro_semanal_recomendado(self):
        """Calcula cuánto se debe ahorrar por semana para alcanzar la meta"""
        if self.dias_restantes <= 0:
            return self.monto_restante
        
        from decimal import Decimal
        semanas_restantes = max(Decimal(str(self.dias_restantes)) / Decimal('7'), Decimal('1'))
        return self.monto_restante / semanas_restantes
    
    @property
    def esta_completada(self):
        """Verifica si la meta está completada"""
        return self.monto_ahorrado >= self.monto_objetivo
    
    @property
    def esta_vencida(self):
        """Verifica si la meta está vencida"""
        from datetime import date
        return self.fecha_objetivo < date.today() and not self.esta_completada
    
    def agregar_ahorro(self, monto):
        """Agrega un monto al ahorro de la meta"""
        self.monto_ahorrado += monto
        if self.esta_completada and self.estado == 'activa':
            self.estado = 'completada'
        self.save()
    
    def calcular_progreso_tiempo(self):
        """Calcula el progreso basado en el tiempo transcurrido"""
        from datetime import date
        fecha_inicio = self.fecha_creacion.date()
        fecha_actual = date.today()
        
        if self.fecha_objetivo <= fecha_inicio:
            return 100
        
        dias_totales = (self.fecha_objetivo - fecha_inicio).days
        dias_transcurridos = (fecha_actual - fecha_inicio).days
        
        from decimal import Decimal
        return min((Decimal(str(dias_transcurridos)) / Decimal(str(dias_totales))) * Decimal('100'), Decimal('100')) if dias_totales > 0 else Decimal('100')