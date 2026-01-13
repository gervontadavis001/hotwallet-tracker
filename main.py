import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from datetime import datetime

st.set_page_config(page_title="🔥 핫월렛 트래커", layout="wide")

# ==========================================
# Helius API 키 (Streamlit Secrets에서 로드)
# ==========================================
HELIUS_API_KEY = st.secrets.get("HELIUS_API_KEY", "")

# ==========================================
# 다중 RPC URLs
# ==========================================
RPC_URLS = {
    'ETH': [
        "https://eth.llamarpc.com",
        "https://ethereum.publicnode.com",
        "https://rpc.ankr.com/eth",
        "https://eth-mainnet.public.blastapi.io",
        "https://rpc.flashbots.net",
        "https://eth.drpc.org",
        "https://1rpc.io/eth",
    ],
    'BSC': [
        "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.binance.org",
        "https://bsc-dataseed2.binance.org",
        "https://bsc.publicnode.com",
    ],
    'ARB': [
        "https://arb1.arbitrum.io/rpc",
        "https://arbitrum.llamarpc.com",
        "https://arbitrum-one.publicnode.com",
        "https://rpc.ankr.com/arbitrum",
    ],
    'BASE': [
        "https://mainnet.base.org",
        "https://base.llamarpc.com",
        "https://base.publicnode.com",
        "https://rpc.ankr.com/base",
    ],
    'OP': [
        "https://mainnet.optimism.io",
        "https://optimism.llamarpc.com",
        "https://optimism.publicnode.com",
        "https://rpc.ankr.com/optimism",
    ],
    'AVAX': [
        "https://api.avax.network/ext/bc/C/rpc",
        "https://rpc.ankr.com/avalanche",
        "https://avalanche.publicnode.com",
    ],
    'POL': [
        "https://polygon-rpc.com",
        "https://polygon.llamarpc.com",
        "https://polygon.publicnode.com",
        "https://rpc.ankr.com/polygon",
    ],
    'SOL': [
        # Helius API가 있으면 우선 사용
    ],
    'SUI': [
        "https://fullnode.mainnet.sui.io:443",
    ],
}

# Helius API 키가 있으면 SOL RPC에 추가
if HELIUS_API_KEY:
    RPC_URLS['SOL'] = [
        f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}",
    ]
else:
    RPC_URLS['SOL'] = [
        "https://rpc.ankr.com/solana",
        "https://solana.drpc.org",
        "https://api.mainnet-beta.solana.com",
    ]

EXPLORER = {
    'ETH': 'https://etherscan.io/address/',
    'BSC': 'https://bscscan.com/address/',
    'ARB': 'https://arbiscan.io/address/',
    'BASE': 'https://basescan.org/address/',
    'OP': 'https://optimistic.etherscan.io/address/',
    'AVAX': 'https://snowtrace.io/address/',
    'POL': 'https://polygonscan.com/address/',
    'SOL': 'https://solscan.io/account/',
    'SUI': 'https://suiscan.xyz/mainnet/account/',
}

COINGECKO_PLATFORM = {
    'ETH': 'ethereum',
    'BSC': 'binance-smart-chain',
    'ARB': 'arbitrum-one',
    'BASE': 'base',
    'OP': 'optimistic-ethereum',
    'AVAX': 'avalanche',
    'POL': 'polygon-pos',
    'SOL': 'solana',
    'SUI': 'sui'
}

# ==========================================
# 지갑 데이터
# ==========================================
WALLETS = {
    'ETH': [
        {
            "addr": "0x28c6c06298d514db089934071355e5743bf21d60",
            "name": "바이낸스 메인핫 #14",
            "main": True
        },
        {
            "addr": "0x21a31ee1afc51d94c2efccaa2092ad1028285549",
            "name": "바이낸스 메인핫 #15",
            "main": True
        },
        {
            "addr": "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",
            "name": "바이낸스 핫 #16",
            "main": False
        },
        {
            "addr": "0x9696f59e4d72e237be84ffd425dcad154bf96976",
            "name": "바이낸스 핫 #18",
            "main": False
        },
        {
            "addr": "0xF977814e90dA44bFA03b6295A0616a897441aceC",
            "name": "바이낸스 콜드 #20",
            "main": False
        },
        {
            "addr": "0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d",
            "name": "바이낸스 콜드 #93",
            "main": False
        },
        {
            "addr": "0x8894e0a0c962cb723c1976a4421c95949be2d4e3",
            "name": "바이낸스 콜드 #51",
            "main": False
        },
        {
            "addr": "0x5a52E96BAcdaBb82fd05763E25335261B270Efcb",
            "name": "바이낸스 콜드 #28",
            "main": False
        },
        {
            "addr": "0x91d40e4818f4d4c57b4578d9eca6afc92ac8debe",
            "name": "OKX 메인핫",
            "main": True
        },
        {
            "addr": "0x4a4aaa0155237881fbd5c34bfae16e985a7b068d",
            "name": "OKX 보조핫 #146",
            "main": False
        },
        {
            "addr": "0xdce83237fbf279c4522e7cac4b10428e2b8694da",
            "name": "OKX 콜드",
            "main": False
        },
        {
            "addr": "0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43",
            "name": "코인베이스 메인핫",
            "main": True
        },
        {
            "addr": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
            "name": "게이트 메인핫",
            "main": True
        },
        {
            "addr": "0xD13C536e71698e189329e9583BE8b67817E045b0",
            "name": "게이트 콜드",
            "main": False
        },
        {
            "addr": "0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23",
            "name": "비트겟 메인핫 #6",
            "main": True
        },
        {
            "addr": "0x97b9D2102A9a65A26E1EE82D59e42d1B73B68689",
            "name": "비트겟 핫 #3",
            "main": False
        },
        {
            "addr": "0x0639556f03714a74a5feeaf5736a4a64ff70d206",
            "name": "비트겟 핫 #4",
            "main": False
        },
        {
            "addr": "0x5bdf85216ec1e38d6458c870992a69e38e03f7ef",
            "name": "비트겟 핫 #5",
            "main": False
        },
        {
            "addr": "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "name": "바이비트 메인핫",
            "main": True
        },
        {
            "addr": "0xA31231E727Ca53Ff95f0D00a06C645110c4aB647",
            "name": "바이비트 핫 #2",
            "main": False
        },
        {
            "addr": "0xad85405cbb1476825b78a021fa9e543bf7937549",
            "name": "바이비트 핫 #3",
            "main": False
        },
        {
            "addr": "0x6522B7F9d481eCEB96557F44753a4b893F837E90",
            "name": "바이비트 핫 #4",
            "main": False
        },
        {
            "addr": "0x187c9fBF5bd0f266883c03f320260C407c7B4100",
            "name": "바이비트 핫 #5",
            "main": False
        },
        {
            "addr": "0xf42aac93ab142090db9fdc0bc86aab73cb36f173",
            "name": "바이비트 메인핫 #173",
            "main": True
        },
        {
            "addr": "0xa03400e098f4421b34a3a44a1b4e571419517687",
            "name": "HTX 메인핫",
            "main": True
        },
        {
            "addr": "0x9642b23ed1e01df1092b92641051881a322f5d4e",
            "name": "MEXC 메인핫",
            "main": True
        },
        {
            "addr": "0x5f65f7b609678448494de4c87521cdf6cef1e932",
            "name": "제미니 핫",
            "main": False
        },
        {
            "addr": "0x5b71d5fd6bb118665582dd87922bf3b9de6c75f9",
            "name": "크립토닷컴 핫 #21",
            "main": False
        },
        {
            "addr": "0x46340b20830761efd32832a74d7169b29feb9758",
            "name": "크립토닷컴 핫 #12",
            "main": False
        },
        {
            "addr": "0xd91efec7e42f80156d1d9f660a69847188950747",
            "name": "쿠코인 핫",
            "main": False
        },
        {
            "addr": "0x58edf78281334335effa23101bbe3371b6a36a51",
            "name": "쿠코인 메인핫 #20",
            "main": True
        },
        {
            "addr": "0xf0bc8fddb1f358cef470d63f96ae65b1d7914953",
            "name": "코빗 핫",
            "main": False
        },
        {
            "addr": "0x167a9333bf582556f35bd4d16a7e80e191aa6476",
            "name": "코인원 핫",
            "main": False
        },
        {
            "addr": "0xd49417f37cED33aBA35DDAbf208D5bFcD87b4eBe",
            "name": "플립 핫",
            "main": False
        },
        {
            "addr": "0xFE6D9AF579dEcCeBfC2d8D366C3D667adB696b32",
            "name": "코인엑스 핫",
            "main": False
        },
        {
            "addr": "0x065AC3d33FEC104FBa9f2f4D674AfAA7c4EBcF43",
            "name": "빙엑스 핫",
            "main": False
        },
        {
            "addr": "0x77134cbC06cB00b66F4c7e623D5fdBF6777635EC",
            "name": "비트파이넥스 핫",
            "main": False
        },
        {
            "addr": "0xcBEA7739929cc6A2B4e46A1F6D26841D8d668b9E",
            "name": "해시키 핫",
            "main": False
        },
        {
            "addr": "0x5c5F75B6FbA2903ADf66C7bDdCeA99B4CcE44a8A",
            "name": "크라켄 핫 #28",
            "main": False
        },
        {
            "addr": "0x89e51fA8CA5D66cd220bAed62ED01e8951aa7c40",
            "name": "크라켄 핫 #7",
            "main": False
        },
        {
            "addr": "0xe3031c1bfaa7825813c562cbdcc69d96fcad2087",
            "name": "고팍스 핫",
            "main": False
        },
        {
            "addr": "0x63DFE4e34A3bFC00eB0220786238a7C6cEF8Ffc4",
            "name": "WOO X 핫",
            "main": False
        },
    ],
    'BSC': [
        {
            "addr": "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "name": "바이비트 메인핫",
            "main": True
        },
        {
            "addr": "0xc3121c4ca7402922e025e62e9bb4d5b244303878",
            "name": "바이비트 핫 #2",
            "main": False
        },
        {
            "addr": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
            "name": "게이트 메인핫",
            "main": True
        },
        {
            "addr": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
            "name": "MEXC 핫 #13",
            "main": False
        },
        {
            "addr": "0x32e3e876aa0C1732ed9Efcf9d8615De7afaEF59f",
            "name": "코인엑스 핫",
            "main": False
        },
        {
            "addr": "0xFE6D9AF579dEcCeBfC2d8D366C3D667adB696b32",
            "name": "코인엑스 핫(대형)",
            "main": False
        },
        {
            "addr": "0xa23EF2319bA4C933eBfDbA80c332664A6Cb13F1A",
            "name": "비트마트 핫",
            "main": False
        },
        {
            "addr": "0xDB861E302EF7B7578A448e951AedE06302936c28",
            "name": "페멕스 핫",
            "main": False
        },
        {
            "addr": "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3",
            "name": "바이낸스 핫 #51",
            "main": False
        },
        {
            "addr": "0x515b72ed8a97f42c568d6a143232775018f133c8",
            "name": "바이낸스 핫 #12",
            "main": False
        },
        {
            "addr": "0xEB2d2F1b8c558a40207669291Fda468E50c8A0bB",
            "name": "바이낸스 핫 #10",
            "main": False
        },
        {
            "addr": "0xF977814e90dA44bFA03b6295A0616a897441aceC",
            "name": "바이낸스 콜드 #20",
            "main": False
        },
        {
            "addr": "0xa180fe01b906a1be37be6c534a3300785b20d947",
            "name": "바이낸스 핫 #16",
            "main": False
        },
        {
            "addr": "0xe2fc31F816A9b94326492132018C3aEcC4a93aE1",
            "name": "바이낸스 출금전용 #7",
            "main": False
        },
        {
            "addr": "0x868f027a5e3bd1cd29606a6681c3ddb7d3dd9b67",
            "name": "비트루 핫",
            "main": False
        },
        {
            "addr": "0x53f78a071d04224b8e254e243fffc6d9f2f3fa23",
            "name": "쿠코인 핫 #2",
            "main": False
        },
        {
            "addr": "0x97b9d2102a9a65a26e1ee82d59e42d1b73b68689",
            "name": "비트겟 핫 #3",
            "main": False
        },
        {
            "addr": "0x0639556f03714a74a5feeaf5736a4a64ff70d206",
            "name": "비트겟 핫 #4",
            "main": False
        },
        {
            "addr": "0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23",
            "name": "비트겟 메인핫 #6",
            "main": True
        },
        {
            "addr": "0xf5988713400DA6fC8A58EC9515e2b0DF9B40B115",
            "name": "OKX 핫",
            "main": True
        },
        {
            "addr": "0xCD47f02B261426Ab734Be9271156327327407E43",
            "name": "플립 핫",
            "main": False
        },
        {
            "addr": "0xdd3CB5c974601BC3974d908Ea4A86020f9999E0c",
            "name": "HTX 핫 #72",
            "main": False
        },
        {
            "addr": "0x6A276a58C5194eF196B58442f627Dba070CB37BF",
            "name": "해시키 핫",
            "main": False
        },
        {
            "addr": "0x065AC3d33FEC104FBa9f2f4D674AfAA7c4EBcF43",
            "name": "빙엑스 핫",
            "main": False
        },
        {
            "addr": "0x983873529f95132BD1812A3B52c98Fb271d2f679",
            "name": "어센덱스 핫",
            "main": False
        },
        {
            "addr": "0x63DFE4e34A3bFC00eB0220786238a7C6cEF8Ffc4",
            "name": "WOO X 핫",
            "main": False
        },
    ],
    'ARB': [
        {
            "addr": "0xb38e8c17e38363af6ebdcb3dae12e0243582891d",
            "name": "바이낸스 핫 #54",
            "main": True
        },
        {
            "addr": "0x3931dab967c3e2dbb492fe12460a66d0fe4cc857",
            "name": "바이낸스 핫 #89",
            "main": False
        },
        {
            "addr": "0x25681ab599b4e2ceea31f8b498052c53fc2d74db",
            "name": "바이낸스 핫 #3",
            "main": False
        },
        {
            "addr": "0xAfEE421482FAEa92292ED3ffE29371742542AD72",
            "name": "OKX 핫",
            "main": True
        },
        {
            "addr": "0x03E6FA590CAdcf15A38e86158E9b3D06FF3399Ba",
            "name": "쿠코인 핫 #24",
            "main": False
        },
        {
            "addr": "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "name": "바이비트 메인핫",
            "main": True
        },
        {
            "addr": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
            "name": "게이트 메인핫",
            "main": True
        },
        {
            "addr": "0x5bdf85216ec1e38d6458c870992a69e38e03f7ef",
            "name": "비트겟 핫 #5",
            "main": False
        },
        {
            "addr": "0xa9b686EE77EfC18e7a08c48FA823CAA0cfDd754E",
            "name": "플립 핫 #6",
            "main": False
        },
    ],
    'BASE': [
        {
            "addr": "0x3304e22ddaa22bcdc5fca2269b418046ae7b566a",
            "name": "바이낸스 핫 #73",
            "main": True
        },
        {
            "addr": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
            "name": "게이트 메인핫",
            "main": True
        },
        {
            "addr": "0x97b9D2102A9a65A26E1EE82D59e42d1B73B68689",
            "name": "비트겟 핫 #3",
            "main": False
        },
        {
            "addr": "0x4e3ae00E8323558fA5Cac04b152238924AA31B60",
            "name": "MEXC 핫 #15",
            "main": False
        },
        {
            "addr": "0xbaed383ede0e5d9d72430661f3285daa77e9439f",
            "name": "바이비트 핫 #6",
            "main": False
        },
        {
            "addr": "0xc8802feab2fafb48b7d1ade77e197002c210f391",
            "name": "OKX 핫",
            "main": True
        },
    ],
    'OP': [
        {
            "addr": "0xacd03d601e5bb1b275bb94076ff46ed9d753435a",
            "name": "바이낸스 핫 #55",
            "main": True
        },
        {
            "addr": "0xB5216CB558Cb018583bED009EE25cA73Eb27bB1d",
            "name": "OKX 핫",
            "main": True
        },
        {
            "addr": "0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23",
            "name": "비트겟 메인핫 #6",
            "main": True
        },
        {
            "addr": "0x0d0707963952f2fba59dd06f2b425ace40b492fe",
            "name": "게이트 메인핫",
            "main": True
        },
        {
            "addr": "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "name": "바이비트 메인핫",
            "main": True
        },
        {
            "addr": "0xa3f45e619cE3AAe2Fa5f8244439a66B203b78bCc",
            "name": "쿠코인 핫 #26",
            "main": False
        },
        {
            "addr": "0xDF90C9B995a3b10A5b8570a47101e6c6a29eb945",
            "name": "MEXC 핫 #7",
            "main": False
        },
        {
            "addr": "0xC8373EDFaD6d5C5f600b6b2507F78431C5271fF5",
            "name": "코인베이스 핫 #11",
            "main": False
        },
    ],
    'AVAX': [
        {
            "addr": "0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23",
            "name": "비트겟 메인핫 #6",
            "main": True
        },
        {
            "addr": "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
            "name": "바이비트 핫",
            "main": True
        },
        {
            "addr": "0xcddc5d0ebeb71a08fff26909aa6c0d4e256b4fe1",
            "name": "바이낸스 메인핫",
            "main": True
        },
        {
            "addr": "0x4E75e27e5Aa74F0c7A9D4897dC10EF651f3A3995",
            "name": "쿠코인 핫 #32",
            "main": False
        },
        {
            "addr": "0xa77ff0e1C52f58363a53282624C7BaA5fA91687D",
            "name": "후오비 핫",
            "main": False
        },
        {
            "addr": "0x6d8be5cdf0d7dee1f04e25fd70b001ae3b907824",
            "name": "바이낸스 핫 #1",
            "main": False
        },
        {
            "addr": "0x3bce63c6c9abf7a47f52c9a3a7950867700b0158",
            "name": "바이낸스 핫 #2",
            "main": False
        },
        {
            "addr": "0x3dd87411a3754deea8cc52c4cf57e2fc254924cc",
            "name": "코인베이스 핫 #1",
            "main": False
        },
        {
            "addr": "0xe1a0ddeb9b5b55e489977b438764e60e314e917c",
            "name": "코인베이스 핫 #7",
            "main": False
        },
        {
            "addr": "0xC94bb9b883Ab642C1C3Ed07af4E36523e7DaF1Fe",
            "name": "OKX 핫",
            "main": True
        },
    ],
    'POL': [
        {
            "addr": "0xe7804c37c13166fF0b37F5aE0BB07A3aEbb6e245",
            "name": "바이낸스 핫 #48",
            "main": True
        },
        {
            "addr": "0xf89d7b9c864f589bbf53a82105107622b35eaa40",
            "name": "바이비트 메인핫",
            "main": True
        },
        {
            "addr": "0x343d752bB710c5575E417edB3F9FA06241A4749A",
            "name": "OKX 메인핫",
            "main": True
        },
        {
            "addr": "0x0639556F03714A74a5fEEaF5736a4A64fF70D206",
            "name": "비트겟 핫 #4",
            "main": False
        },
        {
            "addr": "0x51E3D44172868Acc60D68ca99591Ce4230bc75E0",
            "name": "MEXC 핫",
            "main": False
        },
        {
            "addr": "0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23",
            "name": "비트겟 핫 #6",
            "main": True
        },
        {
            "addr": "0x9AC5637d295FEA4f51E086C329d791cC157B1C84",
            "name": "쿠코인 핫",
            "main": False
        },
    ],
    'SOL': [
        {
            "addr": "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9",
            "name": "바이낸스 핫 #2",
            "main": False
        },
        {
            "addr": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "name": "바이낸스 핫 #3",
            "main": False
        },
        {
            "addr": "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2",
            "name": "바이비트 핫 #1",
            "main": True
        },
        {
            "addr": "7cAui6ADtxLnpRr2wYvwJWTkzwgmVF2LYKnjKTLx4xR8",
            "name": "바이비트 핫 #2",
            "main": False
        },
        {
            "addr": "u6PJ8DtQuPFnfmwHbGFULQ4u4EgjDiyYKjVEsynXq2w",
            "name": "게이트 핫",
            "main": True
        },
        {
            "addr": "C68a6RCGLiPskbPYtAcsCjhG8tfTWYcoB4JjCrXFdqyo",
            "name": "OKX 핫",
            "main": True
        },
        {
            "addr": "A77HErqtfN1hLLpvZ9pCtu66FEtM8BveoaKbbMoZ4RiR",
            "name": "비트겟 핫",
            "main": True
        },
        {
            "addr": "BmFdpraQhkiDQE6SnfG5omcA1VwzqfXrwtNYBwWTymy6",
            "name": "쿠코인 핫",
            "main": False
        },
        {
            "addr": "ASTyfSima4LLAdDgoFGkgqoKowG1LZFDr9fAQrg7iaJZ",
            "name": "MEXC 핫",
            "main": False
        },
    ],
    'SUI': [
        {
            "addr":
            "0x935029ca5219502a47ac9b69f556ccf6e2198b5e7815cf50f68846f723739cbd",
            "name": "바이낸스 핫 #1",
            "main": True
        },
        {
            "addr":
            "0x60dd01bc037e2c1ea2aaf02187701f9f4453ba323338d2f2f521957065b0984d",
            "name": "바이비트 핫",
            "main": True
        },
        {
            "addr":
            "0x62f36b79d7ea8ae189491854edd9318b29c75346792177b230a95f333ffa53ad",
            "name": "게이트 핫",
            "main": True
        },
        {
            "addr":
            "0x0243946bbef4906a5c7b5aefcb6ec771fcced652cf6a80ea424b091c3c127a9d",
            "name": "OKX 핫",
            "main": True
        },
        {
            "addr":
            "0xce7e1e38f996cdb2c4b78c1d187d23c1001d7b266f181498677672f9b1e24ea0",
            "name": "비트겟 핫",
            "main": True
        },
        {
            "addr":
            "0xc38e308a33c6544657a6c1e3149fc256f0ae71b9546ab0999eee958ad2f15f32",
            "name": "MEXC 핫",
            "main": True
        },
    ],
}

CHAIN_OPTIONS = {
    'ETH': f'ETH - Ethereum ({len(WALLETS["ETH"])}개)',
    'BSC': f'BSC - BNB Chain ({len(WALLETS["BSC"])}개)',
    'ARB': f'ARB - Arbitrum ({len(WALLETS["ARB"])}개)',
    'BASE': f'BASE - Base ({len(WALLETS["BASE"])}개)',
    'OP': f'OP - Optimism ({len(WALLETS["OP"])}개)',
    'AVAX': f'AVAX - Avalanche ({len(WALLETS["AVAX"])}개)',
    'POL': f'POL - Polygon ({len(WALLETS["POL"])}개)',
    'SOL': f'SOL - Solana ({len(WALLETS["SOL"])}개)',
    'SUI': f'SUI - Sui ({len(WALLETS["SUI"])}개)',
}


# ==========================================
# 조회 함수들
# ==========================================
def get_token_info(chain, contract):
    """CoinGecko에서 토큰 정보 조회 (실패시 DexScreener)"""
    # 1. CoinGecko 시도
    try:
        platform = COINGECKO_PLATFORM.get(chain)
        if platform:
            res = requests.get(
                f'https://api.coingecko.com/api/v3/coins/{platform}/contract/{contract.lower()}',
                timeout=10)
            if res.ok:
                data = res.json()
                name = data.get('name', '')
                symbol = data.get('symbol', '').upper()
                price = data.get('market_data', {}).get('current_price',
                                                        {}).get('usd', 0)
                if name and symbol:
                    return {'name': name, 'symbol': symbol, 'price': price}
    except:
        pass

    # 2. DexScreener 폴백
    try:
        chain_map = {
            'ETH': 'ethereum',
            'BSC': 'bsc',
            'ARB': 'arbitrum',
            'BASE': 'base',
            'OP': 'optimism',
            'AVAX': 'avalanche',
            'POL': 'polygon',
            'SOL': 'solana',
            'SUI': 'sui'
        }
        dex_chain = chain_map.get(chain, 'ethereum')
        res = requests.get(
            f'https://api.dexscreener.com/latest/dex/tokens/{contract}',
            timeout=10)
        if res.ok:
            data = res.json()
            if data.get('pairs'):
                pair = data['pairs'][0]
                base = pair.get('baseToken', {})
                return {
                    'name': base.get('name', ''),
                    'symbol': base.get('symbol', '').upper(),
                    'price': float(pair.get('priceUsd', 0) or 0)
                }
    except:
        pass

    return {'name': '', 'symbol': '', 'price': 0}


def get_evm_decimals(chain, contract):
    """EVM 토큰 decimals 조회 (다중 RPC 랜덤)"""
    rpc_list = RPC_URLS.get(chain, []).copy()
    random.shuffle(rpc_list)

    for rpc in rpc_list:
        try:
            payload = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'eth_call',
                'params': [{
                    'to': contract,
                    'data': '0x313ce567'
                }, 'latest']
            }
            res = requests.post(rpc, json=payload, timeout=10)
            if res.ok:
                result = res.json().get('result')
                if result and result != '0x':
                    return int(result, 16)
        except:
            continue
    return 18


def get_evm_balance(chain, wallet, contract, decimals):
    """EVM 토큰 잔고 조회 (다중 RPC 랜덤)"""
    rpc_list = RPC_URLS.get(chain, []).copy()
    random.shuffle(rpc_list)

    for rpc in rpc_list:
        try:
            data = '0x70a08231000000000000000000000000' + wallet[2:].lower()
            payload = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'eth_call',
                'params': [{
                    'to': contract,
                    'data': data
                }, 'latest']
            }
            res = requests.post(rpc, json=payload, timeout=10)
            if res.ok:
                result = res.json().get('result')
                if result and result != '0x':
                    return int(result, 16) / (10**decimals)
        except:
            continue
    return 0


def get_solana_balance(wallet, token_mint):
    """Solana 토큰 잔고 조회 (다중 RPC)"""
    rpc_list = RPC_URLS.get('SOL', []).copy()
    random.shuffle(rpc_list)

    for rpc_url in rpc_list:
        try:
            payload = {
                'jsonrpc':
                '2.0',
                'id':
                1,
                'method':
                'getTokenAccountsByOwner',
                'params':
                [wallet, {
                    'mint': token_mint
                }, {
                    'encoding': 'jsonParsed'
                }]
            }
            res = requests.post(rpc_url, json=payload, timeout=15)
            if res.ok:
                data = res.json()
                if data.get('result', {}).get('value'):
                    token_amount = data['result']['value'][0]['account'][
                        'data']['parsed']['info']['tokenAmount']
                    return float(token_amount.get('uiAmount', 0) or 0)
                return 0
        except:
            continue
    return 0


def get_sui_balance(wallet, coin_type):
    """SUI 토큰 잔고 조회"""
    try:
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'suix_getBalance',
            'params': [wallet, coin_type]
        }
        res = requests.post(RPC_URLS['SUI'][0], json=payload, timeout=10)
        if res.ok:
            result = res.json().get('result')
            if result:
                return int(result.get('totalBalance', 0)) / 1e9
    except:
        pass
    return 0


def fetch_balance(chain, wallet, contract, decimals):
    """체인별 잔고 조회"""
    if chain == 'SOL':
        return get_solana_balance(wallet, contract)
    elif chain == 'SUI':
        return get_sui_balance(wallet, contract)
    else:
        return get_evm_balance(chain, wallet, contract, decimals)


# ==========================================
# CSS 스타일
# ==========================================
st.markdown("""
<style>
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .token-info-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 20px;
    }
    .token-name {
        font-size: 20px;
        font-weight: bold;
        color: white;
    }
    .token-price {
        color: #22c55e;
        font-size: 14px;
    }
    .stats-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stat-value {
        font-size: 28px;
        font-weight: bold;
    }
    .stat-label {
        font-size: 12px;
        color: #888;
    }
    .main-wallet {
        color: #eab308 !important;
        font-weight: bold;
    }
    .stDataFrame {
        background: #1a1a2e;
    }
</style>
""",
            unsafe_allow_html=True)

# ==========================================
# UI
# ==========================================
# 세션 상태 초기화
if 'last_search' not in st.session_state:
    st.session_state.last_search = None

# 헤더
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.markdown("# 🔥 핫월렛 트래커")
with col_refresh:
    refresh_clicked = st.button("🔄 새로고침", type="secondary")
    st.caption(f"업데이트: {datetime.now().strftime('%H:%M:%S')}")

# 입력 영역
col1, col2 = st.columns([2, 5])
with col1:
    chain = st.selectbox('체인',
                         list(CHAIN_OPTIONS.keys()),
                         format_func=lambda x: CHAIN_OPTIONS[x],
                         label_visibility="collapsed")
with col2:
    contract = st.text_input('토큰 컨트랙트 주소',
                             placeholder='컨트랙트 주소 입력 후 엔터',
                             label_visibility="collapsed")

# 새로고침 클릭시 이전 검색 재실행
if refresh_clicked and st.session_state.last_search:
    chain = st.session_state.last_search['chain']
    contract = st.session_state.last_search['contract']

# 컨트랙트 주소 입력되면 바로 검색
if contract:
    # 검색 정보 저장
    st.session_state.last_search = {'chain': chain, 'contract': contract}
    # 토큰 정보 조회
    with st.spinner('토큰 정보 조회 중...'):
        token_info = get_token_info(chain, contract)

    # 토큰 정보 표시 (없어도 컨트랙트 표시)
    token_name = token_info['name'] if token_info['name'] else '알 수 없음'
    token_symbol = token_info['symbol'] if token_info[
        'symbol'] else contract[:8] + '...'
    token_price = token_info['price'] if token_info['price'] else 0

    st.markdown(f"""
    <div class="token-info-box">
        <span class="token-name">{token_name} ({token_symbol})</span><br>
        <span class="token-price">가격: ${token_price:,.6f}</span>
    </div>
    """,
                unsafe_allow_html=True)

    # Decimals 조회 (EVM)
    decimals = 18
    if chain not in ['SOL', 'SUI']:
        decimals = get_evm_decimals(chain, contract)

    wallets = WALLETS.get(chain, [])
    results = []

    # 진행 상황
    progress_bar = st.progress(0)
    status_text = st.empty()

    # ★ SOL도 병렬 처리 (Helius API 사용시)
    # 워커 수: Helius면 6개, 공개 RPC면 3개
    sol_workers = 6 if HELIUS_API_KEY else 3

    with ThreadPoolExecutor(max_workers=10 if chain != 'SOL' else sol_workers) as executor:
        futures = {
            executor.submit(fetch_balance, chain, w['addr'], contract, decimals): w
            for w in wallets
        }

        completed = 0
        for future in as_completed(futures):
            w = futures[future]
            try:
                balance = future.result()
            except:
                balance = 0

            usd = balance * token_info['price']
            results.append({
                'name': w['name'],
                'addr': w['addr'],
                'main': w['main'],
                'balance': balance,
                'usd': usd
            })

            completed += 1
            progress_bar.progress(completed / len(wallets))
            status_text.text(f'조회 중... ({completed}/{len(wallets)})')

    progress_bar.empty()
    status_text.empty()

    # 정렬
    results.sort(key=lambda x: x['balance'], reverse=True)

    # 통계
    total_balance = sum(r['balance'] for r in results)
    total_usd = sum(r['usd'] for r in results)
    wallet_count = sum(1 for r in results if r['balance'] > 0)

    # 통계 표시
    st.markdown(f"""
    <div class="stats-box">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center;">
            <div>
                <div class="stat-label">총 잔고</div>
                <div class="stat-value">{total_balance:,.4f}</div>
            </div>
            <div>
                <div class="stat-label">총 USD</div>
                <div class="stat-value" style="color: #22c55e;">${total_usd:,.2f}</div>
            </div>
            <div>
                <div class="stat-label">보유 지갑</div>
                <div class="stat-value">{wallet_count}개</div>
            </div>
        </div>
    </div>
    """,
                unsafe_allow_html=True)

    # 테이블 헤더
    cols = st.columns([0.5, 2, 2, 2, 1.5, 0.8])
    cols[0].markdown("**#**")
    cols[1].markdown("**지갑**")
    cols[2].markdown("**주소**")
    cols[3].markdown("**잔고**")
    cols[4].markdown("**USD**")
    cols[5].markdown("**탐색기**")

    st.markdown("---")

    # 테이블 내용
    for i, r in enumerate(results):
        cols = st.columns([0.5, 2, 2, 2, 1.5, 0.8])
        cols[0].write(f"{i+1}")

        if r['main']:
            cols[1].markdown(
                f"<span style='color: #eab308; font-weight: bold;'>{r['name']}</span>",
                unsafe_allow_html=True)
        else:
            cols[1].write(r['name'])

        short_addr = f"{r['addr'][:10]}...{r['addr'][-6:]}"
        cols[2].markdown(
            f"<span style='color: #60a5fa; font-family: monospace;'>{short_addr}</span>",
            unsafe_allow_html=True)
        cols[3].write(f"{r['balance']:,.4f}")
        cols[4].markdown(
            f"<span style='color: #22c55e;'>${r['usd']:,.2f}</span>",
            unsafe_allow_html=True)
        cols[5].markdown(f"[🔍]({EXPLORER[chain]}{r['addr']})")

elif not contract:
    st.info("토큰 컨트랙트 주소를 입력하고 검색하세요")
