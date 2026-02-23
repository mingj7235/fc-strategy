"""
FC Online Division Mapper
실제 Nexon Open API static metadata 기준 division ID 사용.
https://open.api.nexon.com/static/fconline/meta/division.json
"""

# 실제 Nexon 정적 메타데이터 기준 division ID → tier 정보
DIVISION_DATA = [
    {
        'id': 800,  'name': '슈퍼챔피언스',
        'short': 'S.CHP',
        'color': '#FFD700', 'color2': '#FF8C00',
        'bg': 'linear-gradient(135deg, #2a1a00, #3d2800)',
        'border': '#FFD700',
        'text_class': 'text-yellow-400',
        'rank': 1,
    },
    {
        'id': 900,  'name': '챔피언스',
        'short': 'CHP',
        'color': '#FFC107', 'color2': '#FF9800',
        'bg': 'linear-gradient(135deg, #221a00, #332600)',
        'border': '#FFC107',
        'text_class': 'text-amber-400',
        'rank': 2,
    },
    {
        'id': 1000, 'name': '슈퍼챌린지',
        'short': 'S.CHL',
        'color': '#C084FC', 'color2': '#A855F7',
        'bg': 'linear-gradient(135deg, #1a0a2e, #2d1547)',
        'border': '#A855F7',
        'text_class': 'text-purple-400',
        'rank': 3,
    },
    {
        'id': 1100, 'name': '챌린지1',
        'short': 'CHL1',
        'color': '#60A5FA', 'color2': '#3B82F6',
        'bg': 'linear-gradient(135deg, #0a1628, #0f2040)',
        'border': '#3B82F6',
        'text_class': 'text-blue-400',
        'rank': 4,
    },
    {
        'id': 1200, 'name': '챌린지2',
        'short': 'CHL2',
        'color': '#7DD3FC', 'color2': '#38BDF8',
        'bg': 'linear-gradient(135deg, #0a1628, #0c1e38)',
        'border': '#38BDF8',
        'text_class': 'text-sky-400',
        'rank': 5,
    },
    {
        'id': 1300, 'name': '챌린지3',
        'short': 'CHL3',
        'color': '#BAE6FD', 'color2': '#7DD3FC',
        'bg': 'linear-gradient(135deg, #0a1628, #0c1c32)',
        'border': '#7DD3FC',
        'text_class': 'text-sky-300',
        'rank': 6,
    },
    {
        'id': 2000, 'name': '월드클래스1',
        'short': 'WC1',
        'color': '#34D399', 'color2': '#10B981',
        'bg': 'linear-gradient(135deg, #032014, #053320)',
        'border': '#10B981',
        'text_class': 'text-emerald-400',
        'rank': 7,
    },
    {
        'id': 2100, 'name': '월드클래스2',
        'short': 'WC2',
        'color': '#6EE7B7', 'color2': '#34D399',
        'bg': 'linear-gradient(135deg, #032014, #04291a)',
        'border': '#34D399',
        'text_class': 'text-emerald-300',
        'rank': 8,
    },
    {
        'id': 2200, 'name': '월드클래스3',
        'short': 'WC3',
        'color': '#A7F3D0', 'color2': '#6EE7B7',
        'bg': 'linear-gradient(135deg, #032014, #042318)',
        'border': '#6EE7B7',
        'text_class': 'text-green-300',
        'rank': 9,
    },
    {
        'id': 2300, 'name': '프로1',
        'short': 'PRO1',
        'color': '#2DD4BF', 'color2': '#14B8A6',
        'bg': 'linear-gradient(135deg, #021a18, #032824)',
        'border': '#14B8A6',
        'text_class': 'text-teal-400',
        'rank': 10,
    },
    {
        'id': 2400, 'name': '프로2',
        'short': 'PRO2',
        'color': '#5EEAD4', 'color2': '#2DD4BF',
        'bg': 'linear-gradient(135deg, #021a18, #031f1c)',
        'border': '#2DD4BF',
        'text_class': 'text-teal-300',
        'rank': 11,
    },
    {
        'id': 2500, 'name': '프로3',
        'short': 'PRO3',
        'color': '#99F6E4', 'color2': '#5EEAD4',
        'bg': 'linear-gradient(135deg, #021a18, #031c18)',
        'border': '#5EEAD4',
        'text_class': 'text-teal-200',
        'rank': 12,
    },
    {
        'id': 2600, 'name': '세미프로1',
        'short': 'SP1',
        'color': '#94A3B8', 'color2': '#64748B',
        'bg': 'linear-gradient(135deg, #0f1520, #141d2a)',
        'border': '#64748B',
        'text_class': 'text-slate-400',
        'rank': 13,
    },
    {
        'id': 2700, 'name': '세미프로2',
        'short': 'SP2',
        'color': '#CBD5E1', 'color2': '#94A3B8',
        'bg': 'linear-gradient(135deg, #0f1520, #121a26)',
        'border': '#94A3B8',
        'text_class': 'text-slate-300',
        'rank': 14,
    },
    {
        'id': 2800, 'name': '세미프로3',
        'short': 'SP3',
        'color': '#E2E8F0', 'color2': '#CBD5E1',
        'bg': 'linear-gradient(135deg, #0f1520, #111722)',
        'border': '#CBD5E1',
        'text_class': 'text-slate-200',
        'rank': 15,
    },
    {
        'id': 2900, 'name': '유망주1',
        'short': 'YMJ1',
        'color': '#9CA3AF', 'color2': '#6B7280',
        'bg': 'linear-gradient(135deg, #111318, #161a20)',
        'border': '#6B7280',
        'text_class': 'text-gray-400',
        'rank': 16,
    },
    {
        'id': 3000, 'name': '유망주2',
        'short': 'YMJ2',
        'color': '#D1D5DB', 'color2': '#9CA3AF',
        'bg': 'linear-gradient(135deg, #111318, #14181e)',
        'border': '#9CA3AF',
        'text_class': 'text-gray-300',
        'rank': 17,
    },
    {
        'id': 3100, 'name': '유망주3',
        'short': 'YMJ3',
        'color': '#F3F4F6', 'color2': '#D1D5DB',
        'bg': 'linear-gradient(135deg, #111318, #13171c)',
        'border': '#D1D5DB',
        'text_class': 'text-gray-200',
        'rank': 18,
    },
]

_DIVISION_BY_ID = {d['id']: d for d in DIVISION_DATA}


class DivisionMapper:
    """FC Online 디비전 → 티어 정보 변환"""

    @classmethod
    def get_tier_name(cls, division: int) -> str:
        info = _DIVISION_BY_ID.get(division)
        return info['name'] if info else '알 수 없음'

    @classmethod
    def get_division_info(cls, division: int) -> dict:
        """전체 티어 정보 반환 (색상, 아이콘 포함)"""
        info = _DIVISION_BY_ID.get(division)
        if not info:
            return {
                'division': division,
                'tier_name': '알 수 없음',
                'short': '?',
                'color': '#6B7280',
                'color2': '#4B5563',
                'bg': 'linear-gradient(135deg, #111318, #161a20)',
                'border': '#6B7280',
                'text_class': 'text-gray-400',
                'rank': 99,
            }
        return {
            'division': division,
            'tier_name': info['name'],
            'short': info['short'],
            'color': info['color'],
            'color2': info['color2'],
            'bg': info['bg'],
            'border': info['border'],
            'text_class': info['text_class'],
            'rank': info['rank'],
        }

    @classmethod
    def get_tier_info(cls, division: int) -> dict:
        """레거시 호환용"""
        info = cls.get_division_info(division)
        return {
            'division': division,
            'tier_name': info['tier_name'],
            'colors': {
                'text': info['text_class'],
                'bg': '',
                'border': '',
            }
        }
