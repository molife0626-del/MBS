import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# タイトルと説明
# ---------------------------------------------------------
st.title('📦 出荷重量計算アプリ')
st.write('製品（ポリ/ケース）とパレットを選択して、出荷時の総重量を計算します。')

# ---------------------------------------------------------
# 1. マスタデータの読み込み（1つのファイルから複数シートを読む）
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = 'master_data.xlsx'  # ファイル名を指定
    try:
        # シート名を指定して読み込む
        df_products = pd.read_excel(file_path, sheet_name='製品マスター')
        df_pallets = pd.read_excel(file_path, sheet_name='パレットマスター')
        return df_products, df_pallets
    except FileNotFoundError:
        return None, None
    except ValueError as e:
        # シート名が見つからない場合などのエラー
        st.error(f"読み込みエラー: {e}")
        return None, None

df_products, df_pallets = load_data()

# エラー処理
if df_products is None or df_pallets is None:
    st.error("エラー: 'master_data.xlsx' が見つからないか、シート名が間違っています。")
    st.info("Excelファイル名が 'master_data.xlsx' であること、シート名が '製品マスター' と 'パレットマスター' であることを確認してください。")
    st.stop()

# ---------------------------------------------------------
# 2. 入力フォームの作成
# ---------------------------------------------------------

st.header('1. 製品の選択')

# 製品を選ぶ（B列の「品名」を表示）
# 実際のデータに合わせて列名を指定します
selected_product_name = st.selectbox(
    '製品名を選択してください',
    df_products['品名']
)

# 選択された製品の情報を取得
# 該当する行をフィルタリング
product_row = df_products[df_products['品名'] == selected_product_name].iloc[0]

# G列「1ポリ重量」と D列「入り数」を取得
# ※Excelの列ヘッダーの文字と完全に一致させる必要があります
unit_weight = product_row['1ポリ重量'] 
items_per_pack = product_row['入り数']

# ユーザーへの情報表示
st.info(f"情報: 1ポリあたりの入り数 = {items_per_pack} 個 / 重量 = {unit_weight} kg")

# 数量入力
# G列が「1ポリ重量」なので、ここでの入力は「ポリ数（ケース数）」とします
quantity = st.number_input('出荷する数量（ポリ/ケース数）を入力してください', min_value=1, value=10, step=1)


st.header('2. パレットの選択')

# パレットを選ぶ
# パレットマスター側の列名も確認してください（ここでは仮に「パレット名」「重量kg」としています）
# もしExcel側の列名が違う場合は、ここの文字を変更してください
try:
    selected_pallet_name = st.selectbox(
        '使用するパレットを選択してください',
        df_pallets['パレット名']
    )
    pallet_row = df_pallets[df_pallets['パレット名'] == selected_pallet_name].iloc[0]
    pallet_weight = pallet_row['重量kg']
    
    st.info(f"パレット重量: {pallet_weight} kg")

except KeyError:
    st.error("エラー: パレットマスターの列名がコードと一致していません。「パレット名」「重量kg」という列を作ってください。")
    st.stop()

# ---------------------------------------------------------
# 3. 計算と結果表示
# ---------------------------------------------------------
st.markdown('---')

# 計算ロジック
# 総重量 = (1ポリ重量 × ポリ数) + パレット重量
products_total_weight = unit_weight * quantity
total_weight = products_total_weight + pallet_weight

st.header('📊 計算結果')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("製品重量 (合計)", f"{products_total_weight:.2f} kg")
    st.caption(f"{unit_weight}kg × {quantity}ポリ")

with col2:
    st.metric("パレット重量", f"{pallet_weight:.2f} kg")

with col3:
    st.metric("出荷総重量", f"{total_weight:.2f} kg", delta_color="normal")

st.success("計算が完了しました！")
