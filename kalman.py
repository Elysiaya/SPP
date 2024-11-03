import numpy as np

def kalman_filter(X:np.array,P:np.array,F:np.array,Q:np.array,R:np.array,Z:np.array,H:np.array):
    """
    卡尔曼滤波,其中状态转移方程为
    X(k)=F*X(k-1)+Q
    测量方程为
    Z(k)=H*X(k)+R
    :param X:上一时刻的最佳估值
    :param Q:过程噪声
    :param F:状态转移矩阵
    :param R:观测噪声
    :param Z:观测值
    :param H:观测值转移矩阵
    :return:X 最佳估值,P 协方差矩阵 
    """

    # 预测
    X_ = F @ X
    P_ = F @ P @ F.T + Q

    # 更新过程
    # 求解卡尔曼增益
    K = P_ @ H.T @ np.linalg.inv(H @ P_ @ H.T + R)
    # 求解最佳估值
    X = X_ + K @ (Z - H @ X_)
    # 更新协方差矩阵
    P = (np.eye((K @ H).shape[0]) - K @ H ) @ P_

    return X,P




