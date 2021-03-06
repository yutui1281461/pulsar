/*******************************************************************************
 * Copyright 2014 Trevor Robinson
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ******************************************************************************/
package com.scurrilous.circe.impl;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;

import java.nio.ByteBuffer;

import org.testng.annotations.Test;

import com.scurrilous.circe.StatefulHash;

import mockit.Expectations;
import mockit.Mocked;

@SuppressWarnings("javadoc")
public class AbstractIncrementalIntHashTest {

    @Mocked
    private AbstractIncrementalIntHash hash;

    @Test
    public void testAsStateful() {
        final byte[] input = new byte[10];
        new Expectations(hash) {
            {
                hash.algorithm();
                hash.length();
                hash.initial();
                result = 42;
                hash.resumeUnchecked(42, input, 2, 4);
                result = 99;
            }
        };
        StatefulHash stateful = hash.createStateful();
        stateful.algorithm();
        stateful.length();
        assertNotEquals(stateful, stateful.createNew());
        stateful.reset();
        stateful.update(input, 2, 4);
        assertEquals(99, stateful.getInt());
    }

    @Test
    public void testCalculateByteArray() {
        final byte[] input = new byte[10];
        new Expectations(hash) {
            {
                hash.initial();
                result = 42;
                hash.resume(42, input);
            }
        };
        hash.calculate(input);
    }

    @Test
    public void testCalculateByteArrayIntInt() {
        final byte[] input = new byte[10];
        new Expectations(hash) {
            {
                hash.initial();
                result = 42;
                hash.resume(42, input, 2, 4);
            }
        };
        hash.calculate(input, 2, 4);
    }

    @Test
    public void testCalculateByteBuffer() {
        final ByteBuffer input = ByteBuffer.allocate(10);
        new Expectations(hash) {
            {
                hash.initial();
                result = 42;
                hash.resume(42, input);
            }
        };
        hash.calculate(input);
    }

    @Test
    public void testResumeIntByteArray() {
        final byte[] input = new byte[10];
        new Expectations(hash) {
            {
                hash.resumeUnchecked(42, input, 0, input.length);
            }
        };
        hash.resume(42, input);
    }

    @Test
    public void testResumeIntByteArrayIntInt() {
        final byte[] input = new byte[10];
        new Expectations(hash) {
            {
                hash.resumeUnchecked(42, input, 2, 4);
            }
        };
        hash.resume(42, input, 2, 4);
    }

    @Test
    public void testResumeIntByteBuffer() {
        final ByteBuffer input = ByteBuffer.allocate(20);
        input.position(5);
        input.limit(15);
        new Expectations(hash) {
            {
                hash.resumeUnchecked(42, input.array(), input.arrayOffset() + 5, 10);
            }
        };
        hash.resume(42, input);
        assertEquals(input.limit(), input.position());
    }

    @Test
    public void testResumeIntReadOnlyByteBuffer() {
        final ByteBuffer input = ByteBuffer.allocate(20).asReadOnlyBuffer();
        input.position(5);
        input.limit(15);
        new Expectations(hash) {
            {
                hash.resumeUnchecked(42, withInstanceOf(byte[].class), 0, 10);
            }
        };
        hash.resume(42, input);
        assertEquals(input.limit(), input.position());
    }
}
