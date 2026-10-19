"""Gera incidentes de exemplo. Uso: `python -m app.seed [--reset]` a partir de `back/`."""

import argparse
import random
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Category, Criticality, Incident, Status, utcnow

SEED_COUNT = 100
SEED_WINDOW_HOURS = 48

HIGHWAYS = [
    ("BR-116", 600), ("BR-101", 420), ("BR-381", 480), ("BR-040", 540), ("BR-153", 520),
    ("BR-262", 380), ("BR-050", 300), ("BR-163", 700), ("BR-277", 200), ("BR-364", 650),
]
DIRECTIONS = ["Pista norte", "Pista sul", "Pista leste", "Pista oeste", "Acostamento", "Ambos os sentidos"]
REPORTERS = [
    "Central de Operações 01", "Central de Operações 02", "Viatura VTR-09", "Viatura VTR-14",
    "Motorista em rota", "Usuário via telefone", "Concessionária local", "Sensor climático SC-03",
    "Sensor climático SC-08", "Câmera de monitoramento CM-21",
]

# (peso Alta, Média, Baixa), títulos e descrições por categoria.
CATALOG: dict[Category, dict] = {
    Category.ACCIDENT_WITH_VICTIMS: {
        "weights": (75, 20, 5),
        "items": [
            ("Colisão com vítimas aguardando socorro", "Colisão entre dois veículos com vítimas presas às ferragens. Equipe de resgate acionada."),
            ("Capotamento de caminhão com ferido", "Caminhão capotado ocupa parte da pista; motorista consciente, com ferimentos leves."),
            ("Atropelamento em trecho urbano da rodovia", "Pedestre atingido ao atravessar a pista. SAMU a caminho do local."),
            ("Abalroamento com múltiplos feridos", "Quatro veículos envolvidos, ao menos três feridos. Trânsito lento nos dois sentidos."),
        ],
    },
    Category.VEHICLE_ACCIDENT: {
        "weights": (20, 55, 25),
        "items": [
            ("Colisão traseira sem vítimas", "Colisão traseira entre carro e caminhão ocupa uma faixa; sem confirmação de vítimas."),
            ("Saída de pista de veículo de carga", "Caminhão saiu da pista e parou no barranco. Aguardando guincho."),
            ("Engavetamento leve em declive", "Três veículos envolvidos em colisão de baixa velocidade, apenas danos materiais."),
            ("Tombamento de carreta sem feridos", "Carreta tombada com a carga espalhada no acostamento; motorista ileso."),
        ],
    },
    Category.MECHANICAL_PROBLEM: {
        "weights": (5, 40, 55),
        "items": [
            ("Pneu furado no acostamento", "Caminhão parado no acostamento com pneu estourado; motorista aguarda socorro mecânico."),
            ("Pane elétrica em ônibus", "Ônibus imobilizado com passageiros a bordo após falha elétrica."),
            ("Superaquecimento de motor", "Veículo de carga parado por superaquecimento, sem impacto no fluxo."),
            ("Falha de freio em descida", "Motorista relata perda de eficiência dos freios e parou na área de escape."),
        ],
    },
    Category.ROAD_BLOCKAGE: {
        "weights": (45, 40, 15),
        "items": [
            ("Carga espalhada ocupa faixas", "Carga caída de carreta ocupa duas faixas e interrompe parcialmente o fluxo."),
            ("Queda de barreira na pista", "Deslizamento de terra obstrui a faixa da direita; equipe de manutenção a caminho."),
            ("Objeto de grande porte na faixa", "Objeto não identificado sobre a pista, relatado por motoristas."),
            ("Interdição por manifestação", "Manifestantes bloqueiam o acesso à rodovia, com fila crescente."),
        ],
    },
    Category.ATYPICAL_WEATHER: {
        "weights": (35, 40, 25),
        "items": [
            ("Neblina intensa reduz visibilidade", "Neblina densa reduz a visibilidade para menos de 30 metros nos dois sentidos."),
            ("Acúmulo de água na pista", "Alagamento parcial na faixa da direita; fluxo preservado em velocidade reduzida."),
            ("Pista escorregadia por granizo", "Chuva de granizo deixou o asfalto escorregadio; veículos reduzem a velocidade."),
            ("Vento forte em viaduto", "Rajadas fortes atingem veículos altos; recomendação de cautela aos motoristas."),
        ],
    },
}

STATUS_WEIGHTS = {Status.OPEN: 45, Status.INVESTIGATING: 30, Status.INCONCLUSIVE: 8, Status.CLOSED: 17}


def build_incidents(count: int = SEED_COUNT, *, rng: random.Random | None = None) -> list[Incident]:
    rng = rng or random.Random(42)
    now = utcnow()
    categories = list(CATALOG)
    incidents: list[Incident] = []
    for index in range(count):
        # Round-robin garante que as cinco categorias apareçam de forma equilibrada.
        category = categories[index % len(categories)]
        spec = CATALOG[category]
        title, description = rng.choice(spec["items"])
        criticality = rng.choices(list(Criticality), weights=spec["weights"])[0]
        status = rng.choices(list(STATUS_WEIGHTS), weights=list(STATUS_WEIGHTS.values()))[0]
        highway, length = rng.choice(HIGHWAYS)
        created_at = now - timedelta(minutes=rng.randint(5, SEED_WINDOW_HOURS * 60))
        incidents.append(
            Incident(
                code=f"SEED-{index}",
                title=title,
                description=description,
                category=category,
                criticality=criticality,
                status=status,
                location=f"{highway}, km {rng.randint(1, length)} — {rng.choice(DIRECTIONS)}",
                reporter=rng.choice(REPORTERS),
                created_at=created_at,
                updated_at=created_at,
                version=1,
            )
        )
    return incidents


def seed_if_empty(db: Session, count: int = SEED_COUNT) -> bool:
    if db.scalar(select(func.count()).select_from(Incident)):
        return False
    incidents = build_incidents(count)
    db.add_all(incidents)
    db.flush()
    for incident in incidents:
        incident.code = f"INC-{incident.id:05d}"
    db.commit()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Popula o banco com incidentes de exemplo.")
    parser.add_argument("--reset", action="store_true", help="apaga todos os incidentes antes de popular")
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        created = seed_if_empty(db)
    print(f"{SEED_COUNT} incidentes criados." if created else "O banco já possui incidentes; nada foi alterado.")


if __name__ == "__main__":
    main()
