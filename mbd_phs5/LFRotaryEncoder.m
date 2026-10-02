classdef LFRotaryEncoder < matlab.System
    %LFROTARYENCODER ロータリーエンコーダの模擬
    %
    %   enc = LFRotaryEncoder('SampleTime', 0.05);
    %   rpm = enc(omega);  % 車輪の角速度 omega [rad/s] で SampleTime [s] 経過
    %
    %   車輪の回転をロータリーエンコーダで計測する様子を模擬します．
    %   実機用の rotary_encoder.py の RotaryEncoder クラスと同じ方法で
    %   回転数 [rpm] を算出するので，実機の計測結果と比較できます．
    %   mbd_phs2，mbd_phs3 の LFRotaryEncoder クラスと同じ計算です．
    %
    %   - フォトインタラプタ出力信号の両エッジを利用し，
    %     EdgesPerCalc 個のエッジの間隔 dt から回転数を算出
    %   - 指数移動平均で平滑化
    %   - Timeout の間エッジが来なければ 0 rpm を返す
    %   - 回転の向きは区別しない（実機と同じ）
    %
    %   Simulink では MATLAB System ブロックとして使えます．
    %
    %   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
    %
    %   All rights reserved 2026 (c) Shogo MURAMATSU

    %#codegen
    properties (Nontunable)
        CountsPerRev = 32     % 1回転あたりのカウント数（スリット数×エッジ数）
        EdgesPerCalc = 4      % 1回の回転数の計算に使うエッジ数
        EmaAlpha = 0.2        % 指数移動平均の平滑化係数（0〜1，新しい値の重み）
        Timeout = 0.5         % エッジが来なければ 0 rpm を返すまでの時間 [s]
        SampleTime = 0.05     % サンプリング周期 [s]
    end

    properties (DiscreteState)
        TimeS       % 時刻 [s]
        AngleRad    % 車輪の累積回転角（向きは区別しない）[rad]
        Rpm         % 回転数 [rpm]
        T0          % 回転数の計算を始めたエッジの時刻（NaN は未検出）
        K           % T0 からのエッジ数
        LastEdge    % 最後のエッジの時刻（NaN は未検出）
    end

    methods
        function obj = LFRotaryEncoder(varargin)
            setProperties(obj, nargin, varargin{:});
        end
    end

    methods (Access = protected)
        function setupImpl(~)
        end

        function resetImpl(obj)
            obj.TimeS = 0;
            obj.AngleRad = 0;
            obj.Rpm = 0;
            obj.T0 = NaN;
            obj.K = 0;
            obj.LastEdge = NaN;
        end

        function rpm = stepImpl(obj, omega)
            h = obj.SampleTime;
            speed = abs(double(omega));
            angle0 = obj.AngleRad;
            angle1 = angle0 + speed*h;
            % この間に通過したエッジの時刻を求めて，実機と同じ処理を行う
            step = 2*pi/obj.CountsPerRev;
            edge = floor(angle0/step) + 1;
            while edge*step <= angle1
                tEdge = obj.TimeS + (edge*step - angle0)/speed;
                onEdge(obj, tEdge);
                edge = edge + 1;
            end
            obj.AngleRad = angle1;
            obj.TimeS = obj.TimeS + h;
            rpm = readRpm(obj);
        end

        function onEdge(obj, t)
            % エッジ検出時の処理（rotary_encoder.py の _on_edge() と同じ）
            obj.LastEdge = t;
            if isnan(obj.T0)
                obj.T0 = t;
                obj.K = 0;
                return
            end
            obj.K = obj.K + 1;
            if obj.K >= obj.EdgesPerCalc
                dt = t - obj.T0;
                if dt > 0 && obj.CountsPerRev > 0
                    rpmInst = 60*(obj.EdgesPerCalc/dt)/obj.CountsPerRev;
                    if obj.EmaAlpha > 0
                        obj.Rpm = (1 - obj.EmaAlpha)*obj.Rpm + obj.EmaAlpha*rpmInst;
                    else
                        obj.Rpm = rpmInst;
                    end
                end
                obj.T0 = t;
                obj.K = 0;
            end
        end

        function rpm = readRpm(obj)
            % 回転数 [rpm] の読み出し
            if isnan(obj.LastEdge) || (obj.TimeS - obj.LastEdge) > obj.Timeout
                rpm = 0;
            else
                rpm = obj.Rpm;
            end
        end

        function sts = getSampleTimeImpl(obj)
            sts = createSampleTime(obj, 'Type', 'Discrete', 'SampleTime', obj.SampleTime);
        end

        function out = getOutputSizeImpl(~)
            out = [1 1];
        end

        function out = getOutputDataTypeImpl(~)
            out = 'double';
        end

        function out = isOutputComplexImpl(~)
            out = false;
        end

        function out = isOutputFixedSizeImpl(~)
            out = true;
        end

        function flag = isInputSizeMutableImpl(~, ~)
            flag = false;
        end

        function [sz, dt, cp] = getDiscreteStateSpecificationImpl(~, ~)
            sz = [1 1];
            dt = 'double';
            cp = false;
        end
    end
end
