import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# タイトル
# ---------------------------------------------------------
st.title('📦 出荷重量計算アプリ')

# ---------------------------------------------------------
# 1. マスタデータの読み込み
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = 'master_data.xlsx'
    try:
        # シート名を指定して読み込む
        df_products = pd.read_excel(file_path, sheet_name='製品マスター')
        df_pallets = pd.read_excel(file_path, sheet_name='パレットマスター')
        
        # 【修正点】列名の前後にある空白（スペース）を自動削除する
        # これにより "重量kg " のようなミスがあっても読み込めるようになります
        df_products.columns = df_products.columns.str.strip()
        df_pallets.columns = df_pallets.columns.str.strip()

        return df_products, df_pallets
    except FileNotFoundError:
        return None, None
    except Exception as e:
        return None, None

df_products, df_pallets = load_data()

if df_products is None or df_pallets is None:
    st.error("エラー: 'master_data.xlsx' が読み込めません。GitHubにファイルがあるか確認してください。")
    st.stop()

# ---------------------------------------------------------
# デバッグ用：読み込んだ列名を確認する（エラー時のみ表示）
# ---------------------------------------------------------
if 'パレット名' not in df_pallets.columns:
    st.error(f"パレットマスターの列名読み込みエラー。現在認識されている列名: {list(df_pallets.columns)}")
    st.info("Excelの列名が「パレット名」「重量kg」となっているか確認してください。")
    st.stop()

# ---------------------------------------------------------
# タブで機能を切り替え
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📄 個別入力で計算", "📂 ファイル一括アップロード"])

# =========================================================
# タブ1：個別入力モード
# =========================================================
with tab1:
    st.header('製品と数量を指定')
    
    # 製品選択
    selected_product_name = st.selectbox(
        '製品名を選択',
        df_products['品名'],
        key='tab1_product'
    )
    
    # データ取得
    product_row = df_products[df_products['品名'] == selected_product_name].iloc[0]
    unit_weight = product_row['1ポリ重量']
    
    st.info(f"1ポリ重量: {unit_weight} kg")
    
    # 数量入力
    quantity = st.number_input('数量（ポリ数）', min_value=1, value=10, step=1, key='tab1_qty')
    
    # 製品重量の計算
    products_weight_sum = unit_weight * quantity

# =========================================================
# タブ2：一括アップロードモード
# =========================================================
with tab2:
    st.header('リストから一括計算')
    st.write('A列に「型番」、B列に「数量」が入力されたExcelをアップロードしてください。')

    # ファイルアップローダー
    uploaded_file = st.file_uploader("Excelファイルをドラッグ＆ドロップ", type=['xlsx'])
    
    products_weight_sum = 0 # 初期化
    
    if uploaded_file is not None:
        try:
            # アップロードされたファイルを読み込む
            df_upload = pd.read_excel(uploaded_file)
            
            # 列名のチェックとリネーム
            df_upload.columns = ['型番', '数量'] + list(df_upload.columns[2:])
            
            # マスタデータと結合
            df_merged = pd.merge(df_upload, df_products, left_on='型番', right_on='品名', how='left')
            
            # 重量計算
            df_merged['小計重量'] = df_merged['数量'] * df_merged['1ポリ重量']
            
            # 結果表示
            st.dataframe(df_merged[['型番', '数量', '1ポリ重量', '小計重量']])
            
            if df_merged['1ポリ重量'].isnull().any():
                unknown_products = df_merged[df_merged['1ポリ重量'].isnull()]['型番'].tolist()
                st.error(f"以下の製品がマスタに見つかりませんでした: {unknown_products}")
            else:
                products_weight_sum = df_merged['小計重量'].sum()
                st.success(f"リストの製品合計: {products_weight_sum:.2f} kg")
                
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")

# =========================================================
# 共通：パレット選択と最終計算
# =========================================================
st.markdown("---")
st.header('🎨 パレットの選択')

# パレット選択
selected_pallet_name = st.selectbox(
    '使用するパレット',
    df_pallets['パレット名'],
    key='common_pallet'
)

pallet_row = df_pallets[df_pallets['パレット名'] == selected_pallet_name].iloc[0]
pallet_weight = pallet_row['重量kg']

# 最終計算
total_weight = products_weight_sum + pallet_weight

# 結果表示
st.header('📊 最終計算結果')
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("製品重量", f"{products_weight_sum:.2f} kg")
with c2:
    st.metric("パレット重量", f"{pallet_weight:.2f} kg")
with c3:
    st.metric("出荷総重量", f"{total_weight:.2f} kg")
