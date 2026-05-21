import streamlit as st
import numpy as np
import pandas as pd
import random

# Cấu hình giao diện Web
st.set_page_config(page_title="AI RPG Boss Fight Lab", layout="wide")
st.title("⚔️ Học Tăng Cường: Phòng Thí Nghiệm AI Đánh Boss RPG")
st.write("Hãy thử thay đổi luật game, phân tích bộ não AI và tự mình tham gia trận chiến!")

# ================= HIỂN THỊ LUẬT CHƠI TRÊN GIAO DIỆN CHÍNH =================
with st.expander("📖 Xem Luật Chơi Chi Tiết (Mô hình toán học MDP)", expanded=False):
    col_rule1, col_rule2 = st.columns(2)
    with col_rule1:
        st.markdown(r"""
        ### 📊 Trạng thái & Phần thưởng kết thúc
        * **Hệ thống Máu (HP):** Bạn và Boss đều có tối đa **3 HP**. Trận đấu kết thúc ngay khi một bên về 0 HP.
        * **Phần thưởng tối thượng (Terminal Rewards):**
            * **Chiến thắng (Boss HP = 0):** Nhận **+50 điểm**.
            * **Thất bại (Bạn HP = 0):** Bị phạt **-50 điểm**.
        """)
    with col_rule2:
        st.markdown("""
        ### 🎮 Xác suất của các hành động (Actions)
        1. **⚔️ Tấn công (Attack):**
            * **Thành công:** Boss bị trừ 1 HP. Nhận ngay **+2 điểm**.
            * **Thất bại:** Chém trượt, bị Boss phản công, Bạn bị trừ 1 HP và nhận **-2 điểm**.
        2. **💊 Bơm máu (Heal):**
            * **Thành công:** Bạn được hồi 1 HP (tối đa 3 HP). Nhận **0 điểm**.
            * **Thất bại:** Bị Boss đánh lén lúc sơ hở, Bạn bị trừ 1 HP và nhận **-2 điểm**.
        """)

# ================= TẠO THANH TRƯỢT TƯƠNG TÁC (SIDEBAR) =================
st.sidebar.header("🕹️ Thiết kế Luật Game")
gamma = st.sidebar.slider(r"Hệ số nhìn xa trông rộng ($\gamma$)", 0.0, 0.99, 0.9, 0.05)
st.sidebar.markdown("---")
hit_chance = st.sidebar.slider("🗡️ Tỷ lệ chém trúng Boss", 0.1, 1.0, 0.5, 0.1)
heal_chance = st.sidebar.slider("💊 Tỷ lệ bơm máu thành công", 0.1, 1.0, 0.7, 0.1)

# ================= THUẬT TOÁN VALUE ITERATION (BỘ NÃO AI) =================
def solve_boss_fight(gamma, hit_chance, heal_chance):
    V = np.zeros((4, 4))
    for b in range(1, 4): V[0, b] = -50  # Bạn chết
    for p in range(1, 4): V[p, 0] = 50   # Boss chết
    V[0, 0] = 0
    
    for _ in range(100):
        V_new = np.copy(V)
        for p in range(1, 4):
            for b in range(1, 4):
                q_attack = hit_chance * (2 + gamma * V[p, b-1]) + (1 - hit_chance) * (-2 + gamma * V[p-1, b])
                p_heal = min(3, p + 1)
                q_heal = heal_chance * (0 + gamma * V[p_heal, b]) + (1 - heal_chance) * (-2 + gamma * V[p-1, b])
                V_new[p, b] = max(q_attack, q_heal)
        V = V_new
        
    policy = np.full((4, 4), '', dtype=object)
    for p in range(1, 4):
        for b in range(1, 4):
            q_attack = hit_chance * (2 + gamma * V[p, b-1]) + (1 - hit_chance) * (-2 + gamma * V[p-1, b])
            p_heal = min(3, p + 1)
            q_heal = heal_chance * (0 + gamma * V[p_heal, b]) + (1 - heal_chance) * (-2 + gamma * V[p-1, b])
            policy[p, b] = '⚔️ Đánh' if q_attack > q_heal else '💊 Bơm máu'
            
    return V[1:4, 1:4], policy[1:4, 1:4]

V_star, Pi_star = solve_boss_fight(gamma, hit_chance, heal_chance)

# ================= CHIA TABS GIAO DIỆN CHÍNH =================
tab1, tab2 = st.tabs(["🎮 Chế Độ Người Chơi vs Boss","🔬 Phân Tích Kỹ Thuật AI"])

# --- TAB 1: PHÂN TÍCH AI (Giữ nguyên logic cũ) ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(r"1. Bảng Giá Trị $V^*$ (Giá trị tích lũy kỳ vọng)")
        df_v = pd.DataFrame(V_star, columns=['Boss 1 HP', 'Boss 2 HP', 'Boss 3 HP'], index=['Bạn 1 HP', 'Bạn 2 HP', 'Bạn 3 HP'])
        st.dataframe(df_v.style.background_gradient(cmap="Reds", axis=None).format("{:.1f}"), use_container_width=True)
    with col2:
        st.subheader(r"2. Chiến Thuật Tối Ưu $\pi_*$ (Quyết định của AI)")
        df_pi = pd.DataFrame(Pi_star, columns=['Boss 1 HP', 'Boss 2 HP', 'Boss 3 HP'], index=['Bạn 1 HP', 'Bạn 2 HP', 'Bạn 3 HP'])
        def color_action(val):
            color = '#ffcccc' if 'Đánh' in val else '#cce5ff'
            return f'background-color: {color}; color: black; font-weight: bold; text-align: center'
        st.dataframe(df_pi.style.map(color_action), use_container_width=True)

    st.markdown("### 🧠 Phân tích tâm lý AI hiện tại:")
    attack_count = np.sum(Pi_star == '⚔️ Đánh')
    if attack_count == 9:
        st.error("🔥 **AI đang 'Khát Máu' (Berserker):** Tỷ lệ thắng khi đánh rất cao, AI lao lên tấn công bất chấp lượng HP bản thân!")
    elif attack_count <= 3:
        st.info("🛡️ **AI đang 'Rùa Cố Thủ':** Sát thương không an toàn, AI chọn cách bơm máu liên tục chờ thời cơ.")
    else:
        st.success("⚖️ **AI tính toán thực dụng:** Biết tiến biết lùi, tối ưu hóa theo lượng máu đôi bên.")

# --- TAB 2: CHẾ ĐỘ NGƯỜI CHƠI TRỰC TIẾP (ĐÃ FIX LỖI UI) ---
with tab1:
    st.subheader("Trận Chiến Sinh Tử Với Quỷ Vương")
    
    # Khởi tạo trạng thái game nếu chưa có
    if 'player_hp' not in st.session_state:
        st.session_state.player_hp = 3
    if 'boss_hp' not in st.session_state:
        st.session_state.boss_hp = 3
    if 'logs' not in st.session_state:
        st.session_state.logs = ["Trận đấu bắt đầu! Hãy chọn hành động của bạn."]

    # Hàm reset game
    def reset_game():
        st.session_state.player_hp = 3
        st.session_state.boss_hp = 3
        st.session_state.logs = ["Trận đấu đã được thiết lập lại! Lượt mới bắt đầu."]

    # Đánh giá xem game đã kết thúc chưa dựa vào HP
    is_game_over = st.session_state.player_hp <= 0 or st.session_state.boss_hp <= 0

    # Hiển thị thanh máu trực quan (Dùng max(0, hp) để thanh máu không bị lỗi khi HP < 0)
    col_hp1, col_hp2 = st.columns(2)
    with col_hp1:
        st.metric(label="❤️ Máu của BẠN", value=f"{max(0, st.session_state.player_hp)} / 3")
        st.progress(max(0, st.session_state.player_hp) / 3)
    with col_hp2:
        st.metric(label="😈 Máu của BOSS", value=f"{max(0, st.session_state.boss_hp)} / 3")
        st.progress(max(0, st.session_state.boss_hp) / 3)

    st.markdown("---")

    # Xử lý Logic khi người chơi bấm nút (Chỉ hiện nút khi game chưa kết thúc)
    if not is_game_over:
        col_btn1, col_btn2, _ = st.columns([1, 1, 2])
        
        # Lấy quyết định của AI tại trạng thái hiện tại để đối chiếu
        current_ai_move = Pi_star[st.session_state.player_hp - 1, st.session_state.boss_hp - 1]

        with col_btn1:
            if st.button("⚔️ Quyết Định: TẤN CÔNG", use_container_width=True):
                ai_match_msg = f"🤖 AI phân tích: Ở trạng thái này AI cũng chọn **{current_ai_move}**." if current_ai_move == '⚔️ Đánh' else f"🤖 AI phân tích: Bạn chọn Đánh, nhưng AI toán học khuyên nên **{current_ai_move}**!"
                
                if random.random() <= hit_chance:
                    st.session_state.boss_hp -= 1
                    st.session_state.logs.insert(0, f"🟢 Bạn CHÉM TRÚNG! Boss mất 1 HP. \n{ai_match_msg}")
                else:
                    st.session_state.player_hp -= 1
                    st.session_state.logs.insert(0, f"🔴 Bạn CHÉM TRƯỢT! Bị Boss phản công mất 1 HP. \n{ai_match_msg}")
                
                st.rerun() # YÊU CẦU LOAD LẠI UI NGAY LẬP TỨC

        with col_btn2:
            if st.button("💊 Quyết Định: BƠM MÁU", use_container_width=True):
                ai_match_msg = f"🤖 AI phân tích: Ở trạng thái này AI cũng chọn **{current_ai_move}**." if current_ai_move == '💊 Bơm máu' else f"🤖 AI phân tích: Bạn chọn Bơm máu, nhưng AI toán học khuyên nên **{current_ai_move}**!"
                
                if random.random() <= heal_chance:
                    old_hp = st.session_state.player_hp
                    st.session_state.player_hp = min(3, st.session_state.player_hp + 1)
                    healed = st.session_state.player_hp - old_hp
                    st.session_state.logs.insert(0, f"🔵 Bơm máu THÀNH CÔNG! Hồi {healed} HP. \n{ai_match_msg}")
                else:
                    st.session_state.player_hp -= 1
                    st.session_state.logs.insert(0, f"🔴 Bơm máu THẤT BẠI! Bị đánh lén mất 1 HP. \n{ai_match_msg}")
                
                st.rerun() # YÊU CẦU LOAD LẠI UI NGAY LẬP TỨC

    # Giao diện khi game kết thúc
    else:
        if st.session_state.boss_hp <= 0 and st.session_state.player_hp > 0:
            st.balloons()
            st.success("🏆 CHIẾN THẮNG! Bạn đã hạ gục Quỷ Vương thành công!")
        elif st.session_state.player_hp <= 0 and st.session_state.boss_hp > 0:
            st.error("💀 THẤT BẠI! Bạn đã bị Quỷ Vương đánh bại!")
        else:
            st.warning("💥 HÒA NHAU! Cả hai bên đều gục ngã cùng lúc!")

        if st.button("🔄 Chơi trận mới", type="primary"):
            reset_game()
            st.rerun()

    # Hiển thị nhật ký trận đấu
    st.markdown("### 📜 Nhật ký trận chiến:")
    for log in st.session_state.logs:
        st.write(log)